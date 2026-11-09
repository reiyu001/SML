const gravity: [m/s^2] = 9.8[m/s^2];
let mass: Mass = 75kg;
let force: [kg*m/s^2] = mass * gravity;
let convertedDistance = 3mi as km;

assert force >= 0N;
print("Force:", force);
print("Distance:", convertedDistance);
