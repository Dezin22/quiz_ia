document.addEventListener("DOMContentLoaded", () => {
  const questionElement = document.getElementById("question");
  const optionsElement = document.getElementById("options");
  const generateBtn = document.getElementById("generate-btn");

  generateBtn.addEventListener("click", async () => {
    questionElement.textContent = "Carregando pergunta...";
    optionsElement.innerHTML = "";

    try {
      const response = await fetch("http://127.0.0.1:8000/generate_question", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      const data = await response.json();

      questionElement.textContent = data.question;
      data.options.forEach((option) => {
        const li = document.createElement("li");
        li.textContent = option;
        optionsElement.appendChild(li);
      });
    } catch (error) {
      questionElement.textContent = "Erro ao carregar a pergunta.";
      console.error("Erro:", error);
    }
  });
});
