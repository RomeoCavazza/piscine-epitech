export function fizzBuzz(num) {
  let results = [];
  for (let i = 1; i <= 18; i++) {
    results.push(
      (i % 3 ? '' : 'Fizz') +
      (i % 5 ? '' : 'Buzz') 
      || i
    );
  }
  console.log(results.join(', '));
}