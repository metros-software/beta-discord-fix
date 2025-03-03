document.addEventListener("DOMContentLoaded", function () {
    if (typeof QWebChannel === "undefined") {
        console.error("QWebChannel не подключен. Убедитесь, что qwebchannel.js загружен.");
        return;
    }

    new QWebChannel(qt.webChannelTransport, function (channel) {
        window.bridge = channel.objects.bridge;

        const actionBtn = document.getElementById("actionBtn");
        const selectedOption = document.getElementById("selectedOption");
        const optionsContainer = document.getElementById("options");

        let selectedFile = '';

        window.bridge.getBatFiles(function (files) {
            const lastSelected = localStorage.getItem("lastSelected");

            files.forEach(file => {
                const option = document.createElement("div");
                const fileName = file.replace(".bat", "");

                const parts = fileName.split(/\(([^)]+)\)/);
                const name = parts[0].trim();
                const tags = parts.slice(1).filter((_, index) => index % 2 === 0);

                const textContainer = document.createElement("span");
                textContainer.textContent = name;

                tags.forEach(tagText => {
                    const tag = document.createElement("span");
                    tag.className = "tag";
                    tag.textContent = tagText.trim();
                    textContainer.appendChild(tag);
                });

                option.appendChild(textContainer);

                if (fileName === lastSelected) {
                    selectedOption.innerHTML = '';
                    selectedOption.appendChild(textContainer.cloneNode(true));
                    selectedFile = file;
                }

                option.addEventListener("click", () => {
                    selectedOption.innerHTML = '';
                    selectedOption.appendChild(textContainer.cloneNode(true));
                    optionsContainer.style.display = "none";
                    localStorage.setItem("lastSelected", fileName);
                    selectedFile = file;
                });

                optionsContainer.appendChild(option);
            });

            if (!lastSelected && files.length > 0) {
                const firstFile = files[0].replace(".bat", "");
                const parts = firstFile.split(/\(([^)]+)\)/);
                const name = parts[0].trim();
                const tags = parts.slice(1).filter((_, index) => index % 2 === 0);

                selectedOption.innerHTML = '';
                const textContainer = document.createElement("span");
                textContainer.textContent = name;

                tags.forEach(tagText => {
                    const tag = document.createElement("span");
                    tag.className = "tag";
                    tag.textContent = tagText.trim();
                    textContainer.appendChild(tag);
                });

                selectedOption.appendChild(textContainer);
                localStorage.setItem("lastSelected", firstFile);
                selectedFile = files[0];
            }
        });

        actionBtn.addEventListener("click", () => {
            if (selectedFile) {
                if (actionBtn.textContent === "Остановить") {
                    window.bridge.runBatFile(selectedFile, function (data) {
                        if (data.success) {
                            showNotification(data.message);
                            actionBtn.textContent = "Запустить";
                            actionBtn.classList.remove("stop");
                            selectedOption.disabled = false;
                        } else {
                            showNotification(`Ошибка: ${data.error}`);
                            actionBtn.textContent = "Остановить";
                            actionBtn.classList.add("stop");
                            selectedOption.disabled = true;
                        }
                    });
                } else {
                    window.bridge.runBatFile(selectedFile, function (data) {
                        if (data.success) {
                            showNotification(data.message);
                            actionBtn.textContent = "Остановить";
                            actionBtn.classList.add("stop");
                            selectedOption.disabled = true;
                        } else {
                            showNotification(`Ошибка: ${data.error}`);
                        }
                    });
                }
            } else {
                showNotification("Выберите режим запуска!");
            }
        });

        selectedOption.addEventListener("click", () => {
            if (!selectedOption.disabled) {
                optionsContainer.style.display = optionsContainer.style.display === "block" ? "none" : "block";
            }
        });

        document.addEventListener("click", (event) => {
            if (!event.target.closest(".custom-combobox")) {
                optionsContainer.style.display = "none";
            }
        });

        document.getElementById("logo").addEventListener("click", function () {
            this.classList.remove("rotate");
            void this.offsetWidth;
            this.classList.add("rotate");
        });

        document.getElementById("logo").addEventListener("animationend", function () {
            this.classList.remove("rotate");
        });

        function checkWinwsProcess() {
            window.bridge.checkWinwsProcess(function (isRunning) {
                if (isRunning) {
                    actionBtn.textContent = "Остановить";
                    actionBtn.classList.add("stop");
                    selectedOption.disabled = true;
                } else {
                    actionBtn.textContent = "Запустить";
                    actionBtn.classList.remove("stop");
                    selectedOption.disabled = false;
                }
            });
        }

        checkWinwsProcess();
        setInterval(checkWinwsProcess, 5000);
    });
});

function showNotification(message, duration = 3000) {
    const notification = document.getElementById("notification");
    const notificationMessage = document.getElementById("notificationMessage");
    
    notificationMessage.textContent = message;
    notification.classList.remove("hidden");
    notification.classList.add("show");

    setTimeout(() => {
        notification.classList.remove("show");
        notification.classList.add("hidden");
    }, duration);
}