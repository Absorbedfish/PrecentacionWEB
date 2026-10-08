async function sendData() {
    const num1 = document.getElementById("num1").value;
    const num2 = document.getElementById("num2").value;

     // Validar que ambos números estén ingresados antes de enviar al servidor
     if (num1 === "" || num2 === "") {
        document.getElementById("result").innerText = "Resultado: ";
        return;
    }
    
    // Enviar datos al servidor Flask
    const response = await fetch("/sumapy", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: `num1=${num1}&num2=${num2}`,
    });
    
    const data = await response.json();
    document.getElementById("result").innerText = "Resultado: " + data.sum_result;
}

async function sendMessage(event) {
    // 🛑 Previene el envío por defecto del formulario para manejarlo con fetch
    event.preventDefault(); 

    const email = document.getElementById("email").value;
    const mensaje = document.getElementById("mensaje").value;
    const resultElement = document.getElementById("result");

    // ✅ Validación correcta
    if (email.trim() === "" || mensaje.trim() === "") {
        resultElement.innerText = "⚠️ Por favor, completa todos los campos.";
        return false; // Evita el envío si la validación falla
    }

    try {
        const response = await fetch("/formulariopy", {
            method: "POST",
            headers: {
                "Content-Type": "application/json", // Usamos JSON para un manejo más moderno y simple
            },
            body: JSON.stringify({ // Convertimos los datos a un string JSON
                email: email,
                mensaje: mensaje,
            }),
        });

        // Manejar la respuesta del servidor
        const data = await response.json();
        resultElement.innerText = "✅ Resultado: " + data.mensaje;
    } catch (error) {
        resultElement.innerText = "❌ Ocurrió un error al enviar el mensaje.";
        console.error("Error:", error);
    }
}