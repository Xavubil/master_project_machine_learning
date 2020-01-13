using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using Microsoft.ML;//Benötigt NuGet-Package Microsoft.ML!
using Microsoft.ML.Data;
using Microsoft.ML.Trainers;
using Microsoft.ML.Transforms;
using Microsoft.ML.Trainers.FastTree;
using Microsoft.ML.Trainers.LightGbm;

namespace Rest_Server_ML
{
    public class MLClass
    {
        public static string currentDir = Path.Combine(Environment.CurrentDirectory, "");
        public static string cacheDir = Path.Combine(currentDir, "cacheDir");
        public static string pathTrainData = Path.Combine(currentDir, "processed_trainingdata.csv");
        public static string trainedModelPath = Path.Combine(currentDir, "trainedModel.zip");

        public static string logPath = Path.Combine(cacheDir, "log.txt");
        public static string evalDatasetPath = Path.Combine(cacheDir, "evalData.txt");

        public static string trainSGD()
        {
            MLContext context = new MLContext();
            System.IO.Directory.CreateDirectory(cacheDir);

            List<DataFormat> training, evaluation;
            float positiveWeight;
            loadFile(pathTrainData, out training, out evaluation, out positiveWeight);

            IDataView traindata = context.Data.LoadFromEnumerable(training);
            IDataView evalData = context.Data.LoadFromEnumerable(evaluation);

            var sgdOptions = new SgdCalibratedTrainer.Options()
            {
                LabelColumnName = "Label",
                FeatureColumnName = "Feature",
                NumberOfIterations = 50,
                LearningRate = 0.01,
                PositiveInstanceWeight = positiveWeight
            };
            
            var pipeline = context.BinaryClassification.Trainers.SgdCalibrated(sgdOptions);

            var model = pipeline.Fit(traindata);

            IDataView transformedEval = model.Transform(evalData);
            var evalMetrics = context.BinaryClassification.Evaluate(transformedEval);

            using (var stream = File.Create(trainedModelPath))
            {
                context.Model.Save(model, traindata.Schema, stream);
            }

            return evalMetrics.Accuracy.ToString() + "%";

        }

        public static string trainFastTree()
        {
            MLContext context = new MLContext();
            System.IO.Directory.CreateDirectory(cacheDir);

            List<DataFormat> training, evaluation;
            float positiveWeight;
            loadFile(pathTrainData, out training, out evaluation, out positiveWeight);

            IDataView traindata = context.Data.LoadFromEnumerable(training);
            IDataView evalData = context.Data.LoadFromEnumerable(evaluation);

            var fastTreeOptions = new FastTreeBinaryTrainer.Options()
            {
                LabelColumnName = "Label",
                FeatureColumnName = "Feature",
                LearningRate = 0.01
            };

            var pipeline = context.BinaryClassification.Trainers.FastTree(fastTreeOptions);

            var model = pipeline.Fit(traindata);

            IDataView transformedEval = model.Transform(evalData);
            var evalMetrics = context.BinaryClassification.Evaluate(transformedEval);

            using (var stream = File.Create(trainedModelPath))
            {
                context.Model.Save(model, traindata.Schema, stream);
            }

            return evalMetrics.Accuracy.ToString() + "%";
        }
        public static string trainSDCA()
        {
            MLContext context = new MLContext();
            System.IO.Directory.CreateDirectory(cacheDir);

            List<DataFormat> training, evaluation;
            float positiveWeight;
            loadFile(pathTrainData, out training, out evaluation, out positiveWeight);

            IDataView traindata = context.Data.LoadFromEnumerable(training);
            IDataView evalData = context.Data.LoadFromEnumerable(evaluation);

            var sdcaOptions = new SdcaLogisticRegressionBinaryTrainer.Options()
            {
                LabelColumnName = "Label",
                FeatureColumnName = "Feature",
                MaximumNumberOfIterations = 50,
                BiasLearningRate = 0.01f,
                PositiveInstanceWeight = positiveWeight
            };

            var pipeline = context.BinaryClassification.Trainers.SdcaLogisticRegression(sdcaOptions);

            var model = pipeline.Fit(traindata);

            IDataView transformedEval = model.Transform(evalData);
            var evalMetrics = context.BinaryClassification.Evaluate(transformedEval);

            using (var stream = File.Create(trainedModelPath))
            {
                context.Model.Save(model, traindata.Schema, stream);
            }

            return evalMetrics.Accuracy.ToString() + "%";
        }


        public static string trainLightGBM()
        {
            MLContext context = new MLContext();
            System.IO.Directory.CreateDirectory(cacheDir);

            List<DataFormat> training, evaluation;
            float positiveWeight;
            loadFile(pathTrainData, out training, out evaluation, out positiveWeight);

            IDataView traindata = context.Data.LoadFromEnumerable(training);
            IDataView evalData = context.Data.LoadFromEnumerable(evaluation);

            var lgbmOptions = new LightGbmBinaryTrainer.Options()
            {
                LabelColumnName = "Label",
                FeatureColumnName = "Feature",
                LearningRate = 0.01,
                WeightOfPositiveExamples = positiveWeight
            };

            var pipeline = context.BinaryClassification.Trainers.LightGbm(lgbmOptions);

            var model = pipeline.Fit(traindata);

            IDataView transformedEval = model.Transform(evalData);
            var evalMetrics = context.BinaryClassification.Evaluate(transformedEval);

            using (var stream = File.Create(trainedModelPath))
            {
                context.Model.Save(model, traindata.Schema, stream);
            }

            return evalMetrics.Accuracy.ToString() + "%";
        }
        public static bool predict(DataFormat dataToPredict)
        {
            MLContext context = new MLContext();
            DataViewSchema predSchema;

            var stream = File.OpenRead(trainedModelPath);
            ITransformer predictionPipeline = context.Model.Load(stream, out predSchema);

            PredictionEngine<DataFormat, PredictionFormat> predictionEngine = context.Model.CreatePredictionEngine<DataFormat, PredictionFormat>(predictionPipeline);
            PredictionFormat prediction = predictionEngine.Predict(dataToPredict);
            stream.Close();

            return prediction.Prediction;
        }
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
                float[] featureVector = new float[10];
                for (int i = 0; i < 10; i++)
                {
                    float.TryParse(splitted[i], System.Globalization.NumberStyles.Any, CultureInfo.GetCultureInfo("en-US"), out featureVector[i]);
                }
                df.featureVector = featureVector;
                df.label = (splitted[10] == "i.O.");
                if (df.label)
                    pos.Add(df);
                else
                    neg.Add(df);
            }
            sr.Close();

            Random random = new Random(1);
            foreach (DataFormat item in pos)
            {
                if (random.NextDouble() < 0.8)
                {
                    training.Add(item);
                    countPositive++;
                }
                else
                {
                    evaluation.Add(item);
                }
            }
            foreach (DataFormat item in neg)
            {
                if (random.NextDouble() < 0.8)
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
    }

    public class DataFormat
    {
        [VectorType(10)]
        [ColumnName("Feature")]
        public float[] featureVector { get; set; }

        [ColumnName("Label")]
        public bool label { get; set; }
    }

    public class PredictionFormat
    {
        [ColumnName("PredictedLabel")]
        public bool Prediction { get; set; }

        public float Probability { get; set; }

        public float Score { get; set; }
    }
}
