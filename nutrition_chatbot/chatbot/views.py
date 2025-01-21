from django.shortcuts import render
from .models import FoodItem
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
import openai 
from django.conf import settings

# Create your views here.

# API 및 연결 초기화
pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index("nutritiondb")
openai.api_key=settings.OPENAI_API_KEY

# 모델 불러오기
embedding_model = SentenceTransformer('jhgan/ko-sroberta-multitask')

def homepage(request):
    return render(request, "homepage.html")

def search_food(request):
    query = request.GET.get("q", "")
    results = []

    if query:
        results = FoodItem.objects.filter(name__icontains=query)

    return render(request, "search.html", {"query": query, "results": results})

def recommend_food(request):
    query = request.GET.get("q", "")
    results = []
    natural_response = ""

    if query:
        query_vector = embedding_model.encode(query).tolist()

        response = index.query(vector=query_vector, top_k=5, namespace="", include_metadata=True)

        for result in response["matches"]:
            results.append({
                "name": result["metadata"].get("name", "N/A"),
                "description": result["metadata"].get("description", "정보 없음"),
                "score": result["score"]
            })

        if results:
            result_summary = "\n".join(
                [f"- {item['name']}: {item['description']}" for item in results]
            )
            prompt = f"""
            사용자 질문: "{query}"
            검색된 식품 정보:
            {result_summary}
            위 정보를 바탕으로 사용자 질문에 대한 친절하고 자연스러운 답변을 작성해 주세요.
            """
            openai_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides food recommendations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            natural_response = openai_response.choices[0].message.content.strip()


    return render(request, "recommend.html", {
        "query": query,
        "results": results,
        "natural_response": natural_response
    })