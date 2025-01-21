from django.db import models

# Create your models here.
class FoodItem(models.Model):
    food_code = models.CharField(max_length=50, unique=True) # 식품코드
    name = models.CharField(max_length=100)                  # 식품명
    category = models.CharField(max_length=50)               # 식품대분류명
    main_category = models.CharField(max_length=50)          # 대표식품명
    nutrient_standard = models.CharField(max_length=20)      # 영양성분함량기준량
    energy = models.FloatField()                             # 에너지(kcal)
    protein = models.FloatField()                            # 단백질(g)
    fat = models.FloatField()                                # 지방(g)
    carbs = models.FloatField()                              # 탄수화물(g)
    sugar = models.FloatField()                              # 당류(g)
    fiber = models.FloatField()                              # 식이섬유(g)
    sodium = models.FloatField()                             # 나트륨(mg)
    cholesterol = models.FloatField()                        # 콜레스테롤(mg)
    saturated_fat = models.FloatField()                      # 포화지방산(g)
    trans_fat = models.FloatField()                          # 트랜스지방산(g)
    weight = models.CharField(max_length=20)                 # 식품중량

    def __str__(self):
        return self.name