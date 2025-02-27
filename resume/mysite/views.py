from django.shortcuts import render
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def index(request):
    return render(request, 'mysite/index.html')

@csrf_exempt  # Remove this if CSRF protection is enabled in the form
def send_message(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        if not name or not email or not subject or not message:
            return JsonResponse({"error": "All fields are required."}, status=400)

        full_message = f"From: {name} ({email})\n\n{message}"

        try:
            send_mail(
                subject=subject,
                message=full_message,
                from_email=email,  
                recipient_list=["khanyilekhanyisani8@gmail.com"], 
                fail_silently=False,
            )
            return JsonResponse({"success": "Message sent successfully!"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)
