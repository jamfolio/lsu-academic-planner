let dragged = null;

document.addEventListener("dragstart", (event) => {
  dragged = event.target;
});

document.querySelectorAll(".semester").forEach((box) => {
  box.addEventListener("dragover", (event) => {
    event.preventDefault();
  });
  box.addEventListener("drop", (event) => {
    event.preventDefault();
    if (!dragged){
      return
    } else if (!dragged.dataset.code && !dragged.classList.contains("slot")) {
      return;
    }

    if (dragged.closest(".palette") != null) {
      if (dragged.classList.contains("used")) {
        return;
      }

      let copy = dragged.cloneNode(true);
      let slot = event.target.closest(".slot");

      if (slot == null) {
        let section = dragged.closest("details").dataset.section;
        slot = box.querySelector(`.slot[data-section="${section}"]`);
      }

      if (slot != null) {
        slot.replaceWith(copy);
      } else {
        box.appendChild(copy);
      }

      document
        .querySelectorAll(`.palette .chip[data-code="${dragged.dataset.code}"]`)
        .forEach((chip) => {
          chip.classList.add("used");
        });
    } else {
      box.appendChild(dragged);
    }

    updateHours();
  });
});

document.querySelector("form").addEventListener("submit", (event) => {
  let lines = [];

  document.querySelectorAll(".semester").forEach((box) => {
    let chips = box.querySelectorAll(".chip[data-code]");
    let codes = Array.from(chips).map((chip) => chip.dataset.code);

    lines.push(codes.join(","));
  });

  document.querySelector('textarea[name="plan"]').value = lines.join("\n");
});

function updateHours() {
  let total = 0;

  document.querySelectorAll(".semester").forEach((box) => {
    let sum = 0;

    box.querySelectorAll(".chip").forEach((chip) => {
      sum += Number(chip.dataset.hours || 0);
    });

    let span = box.querySelector("h3 span");

    span.textContent = `${sum} hrs`;
    span.classList.remove("over", "under");

    if (sum > 19) {
      span.classList.add("over");
    } else if (sum < 12) {
      span.classList.add("under");
    }

    total += sum;
  });

  document.getElementById("total_hours").textContent = total;
}
