document.addEventListener("DOMContentLoaded", () => {

    // COUNTERS
    const counters = document.querySelectorAll(".counter");

    counters.forEach(counter => {
        const target = +counter.getAttribute("data-target");
        let count = 0;

        const step = Math.ceil(target / 100);

        const update = () => {
            count += step;

            if (count < target) {
                counter.innerText = count + "+";
                requestAnimationFrame(update);
            } else {
                counter.innerText = target + "+";
            }
        };

        update();
    });

    // ONLINE COUNT ANIMATION
    const online = document.getElementById("onlineCount");

    if (online) {
        setInterval(() => {
            let base = 120;
            online.innerText = base + Math.floor(Math.random() * 80);
        }, 3000);
    }

});