using System;
using System.Collections.Generic;
using System.Diagnostics;
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
        public static void loadFile(string path, out List<DataFormat> training, out List<DataFormat> evaluation, out float positiveClassWeight)
        {
            float countPositive = 0;
            float countNegative = 0;

            training = new List<DataFormat>();
            evaluation = new List<DataFormat>();

            List<DataFormat> pos = new List<DataFormat>();
            List<DataFormat> neg = new List<DataFormat>();

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
                if(df.label)
                    pos.Add(df);
                else
                    neg.Add(df);
            }
            sr.Close();

            Random random = new Random(1);
            foreach(DataFormat item in pos)
            {
                if(random.NextDouble() < 0.8)
                {
                    training.Add(item);
                    countPositive++;
                }
                else
                {
                    evaluation.Add(item);
                }
            }
            foreach(DataFormat item in neg)
            {
                if(random.NextDouble() < 0.8)
                {
                    training.Add(item);
                    countNegative++;
                }
                else
                {
                    evaluation.Add(item);
                }
            }
            positiveClassWeight = countNegative / countPositive;
        }
        
        public static string currentDir = Path.Combine(Environment.CurrentDirectory, "../../../");
        public static string cacheDir = Path.Combine(currentDir, "cacheDir");
        public static string pathTrainData = Path.Combine(currentDir, "trainingdata.csv");
        public static string logPath = Path.Combine(cacheDir, "log.txt");
        public static string evalDatasetPath = Path.Combine(cacheDir, "evalData.txt");

        static void Main(string[] args)
        {
            MLContext context = new MLContext();
            System.IO.Directory.CreateDirectory(cacheDir);
            StreamWriter sw = new StreamWriter(logPath);

            List<DataFormat> training, evaluation;
            float positiveWeight;
            loadFile(pathTrainData,out training,out evaluation, out positiveWeight);

            sw.WriteLine("Size training: " + training.Count);
            sw.WriteLine("Size evluation: " + evaluation.Count);
            sw.WriteLine("PositiveWeight: " + positiveWeight);

            IDataView traindata = context.Data.LoadFromEnumerable(training);
            IDataView evalData = context.Data.LoadFromEnumerable(evaluation);

            var options = new SgdCalibratedTrainer.Options()
            {
                LabelColumnName = "Label",
                FeatureColumnName = "Feature",
                NumberOfIterations = 50,
                LearningRate = 0.01,
                PositiveInstanceWeight = positiveWeight
            };

            var pipeline = context.BinaryClassification.Trainers.SgdCalibrated(options);

            Console.WriteLine("Start training...");
            Stopwatch watch = new Stopwatch();
            watch.Start();
            var model = pipeline.Fit(traindata);
            watch.Stop();
            Console.WriteLine("finished training. Time: " + watch.Elapsed.ToString());
            sw.WriteLine("Elapsed time: " + watch.Elapsed.ToString());
            sw.WriteLine();
            int i = 0;
            foreach(var weight in model.Model.SubModel.Weights)
            {
                sw.WriteLine("weight " + i + ": " + weight);
            }

            IDataView transformedEval = model.Transform(evalData);
            /*var cursor = transformedEval.GetRowCursor(transformedEval.Schema);
            cursor.MoveNext();
            StreamWriter swEvalData = new StreamWriter(evalDatasetPath);
            foreach(var col in cursor.Schema)
            {
                swEvalData.Write(col.Name + "\t");
            }
            swEvalData.WriteLine();
            do
            {
                swEvalData.WriteLine(cursor.ToString());
            } while (cursor.MoveNext());
            swEvalData.Close();*/
            var evalMetrics = context.BinaryClassification.Evaluate(transformedEval);

            sw.WriteLine();
            sw.WriteLine(evalMetrics.ConfusionMatrix.GetFormattedConfusionTable());
            sw.WriteLine();

            Console.WriteLine("Accuracy: " + evalMetrics.Accuracy);
            sw.WriteLine("Accuracy: " + evalMetrics.Accuracy);
            Console.WriteLine("LogLoss: " + evalMetrics.LogLoss);
            sw.WriteLine("Logloss: " + evalMetrics.LogLoss);
            sw.Close();
            Console.ReadLine();
        }
    }
}
