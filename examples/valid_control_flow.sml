fn main() {
    let fuel: [kg] = 3kg;

    while (fuel > 0kg) do {
        print("Fuel left:", fuel);
        fuel -= 1kg;
    }

    for (let i: int = 0; i < 3; i++) {
        if (i == 1) then {
            continue;
        }
        print(i);
    }
}
