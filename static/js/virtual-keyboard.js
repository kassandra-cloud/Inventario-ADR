document.addEventListener('DOMContentLoaded', () => {
    let activeInput = null;
    let keyboardVisible = false;
    let shiftActive = false;
    let capsLockActive = false;
    let specialCharsActive = false;

    const keyboardLayout = {
        normal: [
            ['\`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace'],
            ['Tab', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\'],
            ['CapsLock', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', 'Enter'],
            ['Shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 'Shift'],
            ['Espacio', 'Chars']
        ],
        shift: [
            ['~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', 'Backspace'],
            ['Tab', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '{', '}', '|'],
            ['CapsLock', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ':', '"', 'Enter'],
            ['Shift', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', '<', '>', '?', 'Shift'],
            ['Espacio', 'Chars']
        ],
        special: [
            ['¡', '¿', '€', '£', '¥', '¢', '©', '®', '™', '°', '±', '÷', '×', 'Backspace'],
            ['Tab', 'á', 'é', 'í', 'ó', 'ú', 'ñ', 'ü', 'ä', 'ë', 'ï', 'ö', 'Enter'],
            ['CapsLock', 'à', 'è', 'ì', 'ò', 'ù', 'â', 'ê', 'î', 'ô', 'û', 'ç', 'Enter'],
            ['Shift', 'Á', 'É', 'Í', 'Ó', 'Ú', 'Ñ', 'Ü', 'Ä', 'Ë', 'Ï', 'Ö', 'Shift'],
            ['Espacio', 'ABC']
        ]
    };

    const keyboardElement = document.createElement('div');
    keyboardElement.id = 'virtual-keyboard';
    keyboardElement.style.display = 'none';
    keyboardElement.style.position = 'fixed'; // Usar fixed para que no afecte el layout de la página
    keyboardElement.style.bottom = '10px';
    keyboardElement.style.left = '50%';
    keyboardElement.style.transform = 'translateX(-50%)';
    keyboardElement.style.backgroundColor = '#f0f0f0';
    keyboardElement.style.border = '1px solid #ccc';
    keyboardElement.style.borderRadius = '5px';
    keyboardElement.style.padding = '10px';
    keyboardElement.style.zIndex = '10000'; // Asegurar que esté por encima de otros elementos
    keyboardElement.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
    keyboardElement.style.userSelect = 'none'; // Evitar selección de texto en el teclado

    function createKeyboard(layoutType = 'normal') {
        keyboardElement.innerHTML = ''; // Limpiar teclado anterior
        const currentLayout = keyboardLayout[layoutType];

        currentLayout.forEach(row => {
            const rowElement = document.createElement('div');
            rowElement.style.display = 'flex';
            rowElement.style.marginBottom = '5px';
            row.forEach(key => {
                const keyElement = document.createElement('button');
                keyElement.innerHTML = key;
                keyElement.style.padding = '8px 12px';
                keyElement.style.margin = '2px';
                keyElement.style.border = '1px solid #aaa';
                keyElement.style.borderRadius = '3px';
                keyElement.style.backgroundColor = '#fff';
                keyElement.style.cursor = 'pointer';
                keyElement.style.minWidth = '40px'; // Ancho mínimo para teclas
                keyElement.style.textAlign = 'center';
                keyElement.style.fontSize = '1em';

                if (key.length > 1 && key !== '<' && key !== '>' && key !== '&') { // Teclas especiales más anchas
                    keyElement.style.minWidth = '60px';
                    if (key === 'Espacio') keyElement.style.flexGrow = '1'; // Espacio ocupa más
                    if (key === 'Backspace' || key === 'Enter' || key === 'Shift' || key === 'CapsLock' || key === 'Tab' || key === 'Chars' || key === 'ABC') {
                        keyElement.style.backgroundColor = '#d0d0d0';
                    }
                }
                 if ((key === 'Shift' && shiftActive) || (key === 'CapsLock' && capsLockActive) || (key === 'Chars' && specialCharsActive) || (key === 'ABC' && !specialCharsActive)) {
                    keyElement.style.backgroundColor = '#a0a0a0'; // Indicar tecla activa
                }


                keyElement.addEventListener('mousedown', (e) => { // mousedown para evitar perder foco del input
                    e.preventDefault(); // Evitar que el input pierda el foco
                    if (!activeInput) return;

                    const value = keyElement.innerHTML; // Usar innerHTML para decodificar entidades como <

                    switch (value) {
                        case 'Backspace':
                            activeInput.value = activeInput.value.slice(0, -1);
                            break;
                        case 'Enter':
                            // Podríamos simular un submit o nueva línea si es textarea
                            hideKeyboard();
                            break;
                        case 'Espacio':
                            activeInput.value += ' ';
                            break;
                        case 'Tab':
                            activeInput.value += '\t'; // O manejar foco al siguiente input
                            break;
                        case 'Shift':
                            shiftActive = !shiftActive;
                            if (capsLockActive && !shiftActive) createKeyboard(specialCharsActive ? 'special' : 'normal'); // Si CapsLock está activo y se desactiva Shift, volvemos a minúsculas (o layout especial)
                            else if (capsLockActive && shiftActive) createKeyboard(specialCharsActive ? 'special' : 'shift'); // Si CapsLock y Shift activos, mayúsculas (o layout especial con shift)
                            else createKeyboard(specialCharsActive ? 'special' : (shiftActive ? 'shift' : 'normal'));
                            break;
                        case 'CapsLock':
                            capsLockActive = !capsLockActive;
                            shiftActive = capsLockActive; // Shift se activa/desactiva con CapsLock
                            createKeyboard(specialCharsActive ? 'special' : (capsLockActive ? 'shift' : 'normal'));
                            break;
                        case 'Chars':
                            specialCharsActive = true;
                            createKeyboard('special');
                            break;
                        case 'ABC':
                            specialCharsActive = false;
                            createKeyboard(capsLockActive ? 'shift' : 'normal');
                            break;
                        default:
                            activeInput.value += value;
                            if (shiftActive && !capsLockActive) { // Si Shift está activo pero no CapsLock, desactivar Shift después de una tecla
                                shiftActive = false;
                                createKeyboard(specialCharsActive ? 'special' : 'normal');
                            }
                            break;
                    }
                    activeInput.focus(); // Devolver foco al input
                });
                rowElement.appendChild(keyElement);
            });
            keyboardElement.appendChild(rowElement);
        });
    }

    function showKeyboard(inputElement) {
        if (keyboardVisible && activeInput === inputElement) return; // No hacer nada si ya está visible para este input

        activeInput = inputElement;
        keyboardElement.style.display = 'block';
        keyboardVisible = true;
        // Resetear estados al mostrar
        shiftActive = false;
        capsLockActive = false;
        specialCharsActive = false;
        createKeyboard('normal'); // Iniciar con layout normal

        // Lógica para posicionar el teclado sin tapar el input (simplificada)
        // Se podría mejorar para detectar bordes de pantalla
        const inputRect = activeInput.getBoundingClientRect();
        const keyboardHeight = keyboardElement.offsetHeight;
        const spaceBelow = window.innerHeight - inputRect.bottom;
        const spaceAbove = inputRect.top;

        if (spaceBelow < keyboardHeight + 10 && spaceAbove > keyboardHeight + 10) {
            // No hay suficiente espacio abajo, pero sí arriba: colocar arriba del input
            keyboardElement.style.bottom = 'auto';
            keyboardElement.style.top = (inputRect.top - keyboardHeight - 5) + 'px';
        } else {
            // Colocar abajo por defecto o si no hay espacio arriba
            keyboardElement.style.top = 'auto';
            keyboardElement.style.bottom = '10px'; // Posición fija abajo
        }
         // Centrar horizontalmente
        keyboardElement.style.left = '50%';
        keyboardElement.style.transform = 'translateX(-50%)';
    }

    function hideKeyboard() {
        keyboardElement.style.display = 'none';
        keyboardVisible = false;
        activeInput = null;
    }

    document.body.appendChild(keyboardElement);

    // Event listeners para todos los inputs y textareas
    const inputs = document.querySelectorAll('input[type="text"], input[type="password"], input[type="email"], input[type="search"], input[type="tel"], input[type="url"], textarea');
    inputs.forEach(input => {
        input.addEventListener('focus', () => {
            showKeyboard(input);
        });
        // Opcional: input.addEventListener('click', () => showKeyboard(input));
    });

    // Ocultar teclado si se hace clic fuera de un input o del teclado
    document.addEventListener('click', (event) => {
        if (!keyboardVisible) return;

        let targetElement = event.target;
        let isInput = false;
        inputs.forEach(input => {
            if (input === targetElement) {
                isInput = true;
            }
        });

        const isKeyboardClick = keyboardElement.contains(targetElement);

        if (!isInput && !isKeyboardClick) {
            hideKeyboard();
        }
    });
});