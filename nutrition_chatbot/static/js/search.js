function showDetails(foodId) {
    const modal = document.getElementById("modal");
    modal.style.display = "block";
    const modalDetails = document.getElementById("modal-details");

    fetch(`/food/${foodId}/`)
        .then(response => response.json())
        .then(data => {
            modalDetails.innerHTML = `
                <h2>${data.name}</h2>
                <ul>
                    <li><strong>카테고리:</strong> ${data.category}</li>
                    <li><strong>대표 식품명:</strong> ${data.main_category}</li>
                    <li><strong>영양성분 기준량:</strong> ${data.nutrient_standard}</li>
                    <li><strong>칼로리:</strong> ${data.energy} kcal</li>
                    <li><strong>단백질:</strong> ${data.protein} g</li>
                    <li><strong>지방:</strong> ${data.fat} g</li>
                    <li><strong>탄수화물:</strong> ${data.carbs} g</li>
                    <li><strong>당류:</strong> ${data.sugar} g</li>
                    <li><strong>식이섬유:</strong> ${data.fiber} g</li>
                    <li><strong>나트륨:</strong> ${data.sodium} mg</li>
                    <li><strong>콜레스테롤:</strong> ${data.cholesterol} mg</li>
                    <li><strong>포화지방산:</strong> ${data.saturated_fat} g</li>
                    <li><strong>트랜스지방산:</strong> ${data.trans_fat} g</li>
                    <li><strong>중량:</strong> ${data.weight}</li>
                </ul>
            `;
            modal.style.display = "block";
        })
        .catch(error => {
            console.error("세부 정보를 가져오는 중 오류 발생:", error);
        });
}

function closeDetails() {
    const modal = document.getElementById("modal");
    modal.style.display = "none";
}
