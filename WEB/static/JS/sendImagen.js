function clasificarImagnes() {
    const inputComida = document.getElementById('imageInputComida');
    const inputComida2 = document.getElementById('imageInputComida2');
    const inputAnimales = document.getElementById('imageInputAnimales');
    let Val = 0;

    // 1. Detectar qué input tiene la imagen
    if (inputComida.files[0]) Val = 1;
    else if (inputComida2.files[0]) Val = 2;
    else if (inputAnimales.files[0]) Val = 3;

    if (Val === 0) {
        alert("Por favor, selecciona una imagen primero.");
        return;
    }

    // --- IMPORTANTE: LIMPIAR TEXTOS ANTES DE EMPEZAR ---
    // Borramos resultados de modelos anteriores para no confundir
    ['prediction-text1', 'prediction-text2', 'prediction-text3'].forEach(id => {
        const el = document.getElementById(id);
        if(el) el.innerText = "";
    });

    const formData = new FormData();
    // Preparamos el archivo según el Val detectado
    const inputs = [null, inputComida, inputComida2, inputAnimales];
    formData.append('file', inputs[Val].files[0]);
    formData.append('modelo', Val);

    // 2. Feedback Visual
    const preview = document.getElementById('preview' + Val);
    const resultDiv = document.getElementById('resultado-ia' + Val);
    const textElement = document.getElementById('prediction-text' + Val);

    preview.src = URL.createObjectURL(inputs[Val].files[0]);
    resultDiv.style.display = 'block';
    textElement.innerText = "⏳ Procesando nueva imagen...";

    // 3. Envío al servidor de Ubuntu
    fetch('/clasificar_web', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) throw new Error('Error en el servidor');
        return response.json();
    })
    .then(data => {
        console.log("Respuesta fresca:", data);
        // Mostramos el resultado final
        textElement.innerText = "Resultado: " + data.categoria;
    
        // Limpiamos el input para permitir re-subir la misma foto si se desea
        inputs[Val].value = "";
    })
    .catch(error => {
        console.error('Error:', error);
        textElement.innerText = "❌ Error al conectar con el servidor.";
    });
}