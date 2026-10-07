let dragged = null;

document.addEventListener("dragstart", event => { dragged = event.target });

document.querySelectorAll(".semester").forEach((box) => {
    box.addEventListener("dragover", event => { event.preventDefault() });
    box.addEventListener("drop", event => {
        event.preventDefault();
        if (!dragged || !dragged.dataset.code) {
            return
        }

        if (dragged.closest(".palette") != null) {
            if (dragged.classList.contains("used")) {
                return
            }

            let copy = dragged.cloneNode(true)
            let slot = event.target.closest(".slot")
            
            if (slot == null){
                let section = dragged.closest("details").dataset.section;
                slot = box.querySelector(`.slot[data-section="${section}"]`)
            }

            if (slot != null) {
                slot.replaceWith(copy)
            } else {
                box.appendChild(copy)
            }

            document.querySelectorAll(`.palette .chip[data-code="${dragged.dataset.code}"]`).forEach((chip) => {
                chip.classList.add("used")
            })
        } else {
            box.appendChild(dragged)
        }
    });
});

document.querySelector("form").addEventListener("submit", event => {
    let lines = []

    document.querySelectorAll(".semester").forEach((box) => {
        let chips = box.querySelectorAll(".chip[data-code]")
        let codes = Array.from(chips).map(chip => chip.dataset.code)

        lines.push(codes.join(","))
    })
    
    document.querySelector('textarea[name="plan"]').value = lines.join("\n")
})