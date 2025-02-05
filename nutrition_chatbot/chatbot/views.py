from django.shortcuts import render, get_object_or_404
from .models import FoodItem
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
import openai 
from django.conf import settings
from django.http import JsonResponse
from django.core.paginator import Paginator
import os
from dotenv import load_dotenv
import logging

# Create your views here.
load_dotenv()

logging.basicConfig(level=logging.DEBUG)

# API 및 연결 초기화
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("nutritiondb2")
openai.api_key=os.getenv("OPENAI_API_KEY")

# 모델 불러오기
embedding_model = SentenceTransformer('jhgan/ko-sroberta-multitask')

def homepage(request):
    return render(request, "homepage.html")


def search_food(request):
    query = request.GET.get("q", "").strip()

    cal_min = request.GET.get("cal_min")
    cal_max = request.GET.get("cal_max")
    protein_min = request.GET.get("protein_min")
    protein_max = request.GET.get("protein_max")
    fat_min = request.GET.get("fat_min")
    fat_max = request.GET.get("fat_max")
    carbs_min = request.GET.get("carbs_min")
    carbs_max = request.GET.get("carbs_max")
    sugar_min = request.GET.get("sugar_min")
    sugar_max = request.GET.get("sugar_max")
    fiber_min = request.GET.get("fiber_min")
    fiber_max = request.GET.get("fiber_max")
    sodium_min = request.GET.get("sodium_min")
    sodium_max = request.GET.get("sodium_max")

    if not query and not any([cal_min, cal_max, protein_min, protein_max, fat_min, fat_max,
                              carbs_min, carbs_max, sugar_min, sugar_max, fiber_min, fiber_max,
                              sodium_min, sodium_max]):
        return render(request, "search.html", {
            "query": query,
            "results": [],
        })

    results = FoodItem.objects.all()

    if query:
        results = results.filter(name__icontains=query)

    if cal_min:
        results = results.filter(energy__gte=float(cal_min))
    if cal_max:
        results = results.filter(energy__lte=float(cal_max))
    if protein_min:
        results = results.filter(protein__gte=float(protein_min))
    if protein_max:
        results = results.filter(protein__lte=float(protein_max))
    if fat_min:
        results = results.filter(fat__gte=float(fat_min))
    if fat_max:
        results = results.filter(fat__lte=float(fat_max))
    if carbs_min:
        results = results.filter(carbs__gte=float(carbs_min))
    if carbs_max:
        results = results.filter(carbs__lte=float(carbs_max))
    if sugar_min:
        results = results.filter(sugar__gte=float(sugar_min))
    if sugar_max:
        results = results.filter(sugar__lte=float(sugar_max))
    if fiber_min:
        results = results.filter(fiber__gte=float(fiber_min))
    if fiber_max:
        results = results.filter(fiber__lte=float(fiber_max))
    if sodium_min:
        results = results.filter(sodium__gte=float(sodium_min))
    if sodium_max:
        results = results.filter(sodium__lte=float(sodium_max))

    paginator = Paginator(results, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "search.html", {
        "query": query,
        "results": page_obj,
    })

def food_detail_json(request, food_code):
    food = get_object_or_404(FoodItem, id=food_code)

    return JsonResponse({
        "name": food.name,
        "category": food.category,
        "main_category": food.main_category,
        "nutrient_standard": food.nutrient_standard,
        "energy": food.energy,
        "protein": food.protein,
        "fat": food.fat,
        "carbs": food.carbs,
        "sugar": food.sugar,
        "fiber": food.fiber,
        "sodium": food.sodium,
        "cholesterol": food.cholesterol,
        "saturated_fat": food.saturated_fat,
    })

def recommend_food(request):
    query = request.POST.get("question", "").strip()
    natural_response = ""

    logging.debug(f"사용자 입력 질문: {query}")

    if query:
        try:
            query_vector = embedding_model.encode(query).tolist()
            logging.debug(f"벡터화된 질문: {query_vector}")

            response = index.query(vector=query_vector, top_k=5, namespace="", include_metadata=True)
            logging.debug(f"Pinecone 검색 결과: {response}")

            if response.get("matches"):
                result_summary = "\n".join(
                    [f"- {result['metadata'].get('name', 'N/A')}: {result['metadata'].get('description', '정보 없음')}" for result in response["matches"]]
                )
                logging.debug(f"검색된 결과 요약: {result_summary}")

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
                    max_tokens=300,
                    temperature=0.7
                )
                natural_response = openai_response.choices[0].message.content.strip()
                logging.debug(f"OpenAI 응답: {natural_response}")
            else:
                logging.debug("Pinecone에서 일치하는 결과가 없습니다.")
                natural_response = "추천할 결과가 없습니다. 질문을 다시 작성해 주세요."

        except Exception as e:
            logging.error(f"추천 서비스 처리 중 오류 발생: {e}")
            natural_response = "추천 서비스 처리 중 오류가 발생했습니다."

    return render(request, "recommend.html", {
        "query": query,
        "natural_response": natural_response
    })