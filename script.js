const toScreen2Btn = document.getElementById('toScreen2Btn');

toScreen2Btn.addEventListener('click', () => {
window.location.href = 'Formulario2.html';
});
function hablar(texto) {
    const respuesta = new SpeechSynthesisUtterance(texto);
    respuesta.lang = 'es-ES';
    speechSynthesis.speak(respuesta);
  }  
