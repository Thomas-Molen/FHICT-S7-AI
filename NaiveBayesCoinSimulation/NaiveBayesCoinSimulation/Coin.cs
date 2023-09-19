using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using static System.Runtime.InteropServices.JavaScript.JSType;

namespace NaiveBayesCoinSimulation
{
    public class Coin
    {
        private Face topFace;
        private Face bottomFace;

        public Face Top
        {
            get
            {
                return topFace;
            }
        }
        public Face Bottom
        {
            get
            {
                return bottomFace;
            }
        }

        private Face[] faces;
        public Coin(Face face1, Face face2)
        {
            faces = new Face[2] { face1, face2 };
            PopulateFaces();
        }

        private void PopulateFaces()
        {
            // Shuffle faces to ensure an even distribution
            var rng = new Random();
            rng.Shuffle(faces);
            
            topFace = faces[0];
            bottomFace = faces[1];
        }
    }

    public enum Face
    {
        Heads,
        Tails
    }
}
