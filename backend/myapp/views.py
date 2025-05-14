import json
import os
import tempfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from estsum import EstSum
from htmlmuundur import HTMLMuundur

summarizer = EstSum()
HTMLToSGMLConverter = HTMLMuundur()

# Use a non-watched directory, such as /tmp or a custom folder for generated files
temp_file_path = os.path.join("/tmp", "temp.txt")  # or '/generated' folder
generated_file_path = os.path.join("/tmp", "temp_gen.txt")

# Ensure the temp directory exists (optional but good for clarity)
os.makedirs("/tmp", exist_ok=True)


@csrf_exempt
@require_http_methods(["POST"])
def summarize(request):
    try:
        data = json.loads(request.body)
        summarizer.reset_variables()

        HTMLToSGMLConverter.parse_url(data['url'], temp_file_path)
        summarizer.summarize(temp_file_path, generated_file_path, False, data['alpha'], data['beta'], data['gamma'], data['summaryLength']/100)

        return JsonResponse({'success': True, 'title': summarizer.title.text, 'summary': summarizer.summary})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
