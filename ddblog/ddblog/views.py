from django.http import JsonResponse

def test_cors(request):

    return JsonResponse({'code':999})

