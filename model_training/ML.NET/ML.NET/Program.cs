using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using Microsoft.ML;//Benötigt NuGet-Package Microsoft.ML!
using Microsoft.ML.Data;
using Microsoft.ML.Trainers;

namespace ML.NET
{
    class DataFormat
    {
        [VectorType(12)]
        [ColumnName("Feature")]
        public float[] featureVector { get; set; }

        [ColumnName("Label")]
        public bool label { get; set; }
    }

    class Program
    {
        public static List<DataFormat> loadFile(string path)
        {
            List<DataFormat> returner = new List<DataFormat>();

            StreamReader sr = new StreamReader(path);
            string line = sr.ReadLine();
            while (!sr.EndOfStream)
            {
                line = sr.ReadLine();
                string[] splitted = line.Split(',');
                DataFormat df = new DataFormat();
                float[] featureVector = new float[12];
                for (int i = 0; i < 12; i++)
                {
                    float.TryParse(splitted[i], System.Globalization.NumberStyles.Any, CultureInfo.GetCultureInfo("en-US"), out featureVector[i]);
                }
                df.featureVector = featureVector;
                df.label = (splitted[14] == "i.O.");
                returner.Add(df);
            }
            sr.Close();
            return returner;
        }

        public static string currentDir = Path.Combine(Environment.CurrentDirectory, "../../../");
        public static string cacheDir = Path.Combine(currentDir, "cacheDir");
        public static string pathTrainData = Path.Combine(currentDir, "trainingdata.csv");
        public static string logPath = Path.Combine(cacheDir, "log.txt");

        static void Main(string[] args)
        {
            MLContext context = new MLContext();
            var data = loadFile(pathTrainData);
            //TODO seperate training- and evaluation-dataset classwise and (80/20)
            IDataView traindata = context.Data.LoadFromEnumerable(data);
            

            var options = new SgdCalibratedTrainer.Options()
            {
                LabelColumnName = "Label",
                FeatureColumnName = "Feature",
                NumberOfIterations = 30,
                LearningRate = 0.0001
                //TODO weight inputs, based on class (unbalanced dataset)
            };

            var pipeline = context.BinaryClassification.Trainers.SgdCalibrated(options);

            var model = pipeline.Fit();//TODO fit
            //TODO add evaluation
        }
    }
}
