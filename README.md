# EstSum liidese jooksutamiseks

1. Juur kaustas `npm install`
2. **Server kaustas** jooksuta `python -m venv venv` (või `python3 -m venv venv`)
3. `source venv/bin/activate`
4. `python install -r requirements.txt`
5. Backendi käivitamiseks jooksuta **Server kaustas** `python manage.py runserver 8080 --noreload`
6. Frontend käivitamiseks jookusta **Juur kaustas** `npm run dev`
