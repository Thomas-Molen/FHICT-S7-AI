using NaiveBayesCoinSimulation;
using System.Collections.Concurrent;

Console.WriteLine("Enter number of iterations");
int iterations = int.Parse(Console.ReadLine() ?? "0");
Task[] tasks = new Task[iterations];

PredictionTechnique predictionTechnique = (PredictionTechnique)(ConsoleUtil.DisplayMenu("Select prediction method", Enum.GetNames(typeof(PredictionTechnique)).ToArray()) - 1);

Console.Clear();
Console.WriteLine("Simulating...");

ConcurrentBag<bool> results = new ConcurrentBag<bool>();
for (int i = 0; i < iterations; i++)
{
    tasks[i] = Task.Run(() =>
    {
        results.Add(SimulateCoinPrediction(predictionTechnique, new Coin[]
        {
            new Coin(Face.Heads, Face.Heads),
            new Coin(Face.Heads, Face.Tails),
            new Coin(Face.Tails, Face.Tails)
        }));
    });
}
await Task.WhenAll(tasks);

ConsoleUtil.DisplayResults(results.ToArray());
ConsoleUtil.KeepConsoleOpen();

bool SimulateCoinPrediction(PredictionTechnique predictionTechnique, params Coin[] coins)
{
    var coinBag = new CoinBag(coins);
    var coin = coinBag.GetCoin();

    Face prediction;
    switch (predictionTechnique)
    {
        case PredictionTechnique.duplicate:
            prediction = coin.Top;
            break;
        case PredictionTechnique.invert:
            prediction = InvertFace(coin.Top);
            break;
        case PredictionTechnique.random:
            prediction = RandomFace();
            break;
        default:
            throw new ArgumentException("No prediction technique found");
    }
    return prediction == coin.Bottom;
}


Face InvertFace(Face input)
{
    // Shift enum value by 1, wrapping back to 0 at overflow
    return (Face)(((int)input + 1) % Enum.GetValues(typeof(Face)).Length);
}


Face RandomFace()
{
    Random random = new Random();
    return (Face)random.Next(Enum.GetValues(typeof(Face)).Length);
}

enum PredictionTechnique
{
    duplicate,
    invert,
    random
}