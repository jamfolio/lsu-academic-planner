let dragged = null;

document.addEventListener("dragstart", event => { dragged = event.target });

document.querySelectorAll(".semester").forEach((box) => {
    box.addEventListener("dragover", event => { event.preventDefault() });
    box.addEventListener("drop", event => { event.preventDefault(); box.appendChild(dragged) });
});