using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;

namespace NaiveBayesCoinSimulation
{
    public class CoinBag
    {
        private Coin[] coins;
        private Random rng;
        public CoinBag(params Coin[] coins)
        {
            rng = new Random();
            this.coins = coins;
        }

        public Coin GetCoin()
        {
            if (!coins.Any()) throw new ArgumentException("No coins in coin bag");

            rng.Shuffle(coins);
            return coins[0];
        }
    }
}
