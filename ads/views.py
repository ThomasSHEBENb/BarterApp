from django.shortcuts import render, redirect, get_object_or_404
from .forms import AdForm, RegisterForm, ExchangeProposalForm
from .models import Ad, ExchangeProposal, Notification
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

@login_required
def create_ad(request):
    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.user = request.user
            ad.save()
            messages.success(request, "Объявление успешно создано!")
            return redirect('ad_list')
    else:
        form = AdForm()
    return render(request, 'ads/create_ad.html', {'form': form})




def ad_list(request):
    qs = Ad.objects.all().order_by('-created_at')  # Все объявления, начиная с новых

    q = request.GET.get('q')  # Получаем текст запроса (поиск)
    if q:
        # Фильтруем по вхождению текста в заголовок или описание
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q)
        )

    category = request.GET.get('category')  # Получаем выбранную категорию
    if category:
        qs = qs.filter(category=category)

    condition = request.GET.get('condition')  # Получаем выбранное состояние
    if condition:
        qs = qs.filter(condition=condition)

    paginator = Paginator(qs, 10)  # Пагинация: 10 объявлений на страницу
    page_number = request.GET.get('page')  # Текущий номер страницы
    page_obj = paginator.get_page(page_number)  # Получаем объекты текущей страницы

    return render(request, 'ads/ad_list.html', {
        'page_obj': page_obj,  # Страница с объявлениями
        'q': q,  # Чтобы подставить в поле поиска
        'selected_category': category,  # Для отображения выбранной категории
        'selected_condition': condition,  # Для отображения выбранного состояния
        'CATEGORY_CHOICES': Ad._meta.get_field('category').choices,
        'CONDITION_CHOICES': Ad.CONDITION_CHOICES,
    })

def home(request):
    return render(request, 'ads/home.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('ad_list')
    else:
        form = RegisterForm()
    return render(request, 'ads/register.html', {'form': form})

@login_required
def user_ads(request):
    ads = Ad.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'ads/user_ads.html', {'ads': ads})

@login_required
def create_proposal(request, ad_id):
    ad_sender = get_object_or_404(Ad, pk=ad_id) #Проверяет наличие объявления
    user_ads = Ad.objects.filter(user=request.user)
    if not user_ads.exists(): #Обработка ошибок при поптыке обменять что-то не имея объявления
        messages.error(request, "У вас нет объявлений, чтобы предложить обмен.")
        return redirect('ad_detail', pk=ad_id)

    if ad_sender.user == request.user:
        messages.error(request, "Вы не можете обмениваться своими собственными объявлениями.")
        return redirect('ad_detail', pk=ad_id)
    
    existing = ExchangeProposal.objects.filter(
        ad_sender=ad_sender,
        from_user=request.user,
        status='pending'
    ).exists()

    if existing:
        messages.warning(request, "Вы уже предложили обмен по этому объявлению. Ожидайте ответа.")
        return redirect('ad_detail', pk=ad_id)

    if request.method == 'POST':
        form = ExchangeProposalForm(request.POST, user=request.user)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.ad_sender = ad_sender
            proposal.from_user = request.user
            proposal.to_user = ad_sender.user
            proposal.save()
            Notification.objects.create(
                user=ad_sender.user,
                message=f'Вы получили предложение обмена от {request.user.username}.'
            )
            messages.success(request, "Предложение отправлено.")
            return redirect('ad_detail', pk=ad_id)
    else:
        form = ExchangeProposalForm(user=request.user)

    return render(request, 'ads/create_proposal.html', {'form': form, 'ad_sender': ad_sender})




@login_required
def proposal_list(request):
    # Все входящие предложения — это те, где ad_receiver принадлежит текущему пользователю
    received_proposals = ExchangeProposal.objects.filter(ad_sender__user=request.user)
    
    # Отправленные предложения
    sent_proposals = ExchangeProposal.objects.filter(from_user=request.user)

    context = {
        'received_proposals': received_proposals,
        'sent_proposals': sent_proposals,
    }
    return render(request, 'ads/proposal_list.html', context)

@login_required
def accept_proposal(request, pk):
    proposal = get_object_or_404(ExchangeProposal, pk=pk, ad_sender__user=request.user)

    if proposal.status != 'accepted':
        # Отправляем уведомление до удаления
        Notification.objects.create(
            user=proposal.from_user,
            message=f'Ваше предложение обмена было принято.'
        )

        # Сохраняем объявления перед удалением
        ad_sender = proposal.ad_sender
        ad_receiver = proposal.ad_receiver

        # Удаляем объявления
        if ad_sender:
            ad_sender.delete()
        if ad_receiver:
            ad_receiver.delete()

        # Удаляем саму заявку
        proposal.delete()

        messages.success(request, 'Предложение принято. Объявления удалены.')
    else:
        messages.info(request, 'Предложение уже принято.')

    return redirect('proposal_list')



@login_required
def reject_proposal(request, pk):
    proposal = get_object_or_404(ExchangeProposal, pk=pk, ad_sender__user=request.user)
    if proposal.status == 'pending':
        proposal.status = 'rejected'
        proposal.save()
        messages.info(request, 'Предложение отклонено.')
    return redirect('proposal_list')

@login_required
def ad_detail(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    existing_proposal = None

    if request.user.is_authenticated and request.user != ad.user:
        existing_proposal = ExchangeProposal.objects.filter(
            ad_sender=ad,
            from_user=request.user,
            status='pending' 
        ).first()

    return render(request, 'ads/ad_detail.html', {
        'ad': ad,
        'existing_proposal': existing_proposal,
    })

@login_required
def notifications(request):
    notes = request.user.notifications.order_by('-created_at')
    notes.filter(is_read=False).update(is_read=True)
    return render(request, 'ads/notifications.html', {'notifications': notes})
