using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace NaiveBayesCoinSimulation
{
    public static class ConsoleUtil
    {
        public static int DisplayMenu(string title, params string[] options)
        {
            if (options == null || !options.Any())
            {
                throw new ArgumentException("Options list cannot be null or empty.");
            }

            Console.Clear();
            Console.WriteLine(title);

            for (int i = 0; i < options.Count(); i++)
            {
                Console.WriteLine($"{i + 1}. {options[i]}");
            }

            int choice;
            do
            {
                Console.Write("Enter your choice (1-" + options.Count() + "): ");
            } while (!int.TryParse(Console.ReadLine(), out choice) || choice < 1 || choice > options.Count());

            return choice;
        }

        public static void DisplayResults(params bool[] results)
        {
            Console.Clear();
            int resultCount = results.Count();
            Console.WriteLine($"Result count: {resultCount}");
            int correctResults = results.Count(r => r);
            int incorrectResults = results.Count(r => !r);
            Console.WriteLine($"Correct: {correctResults} ({((double)correctResults / (double)resultCount) * 100}%)");
            Console.WriteLine($"Incorrect: {incorrectResults} ({((double)incorrectResults / (double)resultCount) * 100}%)");
        }

        public static void KeepConsoleOpen()
        {
            Console.WriteLine("\nPress any key to exit");
            Console.ReadKey();
        }
    }
}
