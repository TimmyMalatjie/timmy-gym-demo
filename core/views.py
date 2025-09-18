from django.shortcuts import render

def home(request):
    """
    Home screen controller - the main hub of your game world
    """
    context = {
        'page_title': 'Home',
        'active_members': 500,  # Mock data for now
        'weekly_classes': 50,
        'expert_trainers': 10,
        'years_experience': 5,
    }
    return render(request, 'core/home.html', context)