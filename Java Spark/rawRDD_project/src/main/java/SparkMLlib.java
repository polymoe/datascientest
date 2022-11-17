import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import static org.apache.spark.sql.functions.col;
import org.apache.spark.sql.DataFrameNaFunctions;
import java.util.HashMap;
import java.util.Map;

import org.apache.spark.ml.feature.StringIndexer;
import org.apache.spark.ml.feature.StandardScaler;
import org.apache.spark.ml.feature.StandardScalerModel;
import org.apache.spark.ml.feature.VectorAssembler;
import org.apache.spark.ml.classification.LogisticRegression;
import org.apache.spark.ml.classification.LogisticRegressionModel;
import scala.Tuple2;
import org.apache.spark.api.java.JavaRDD;
import org.apache.spark.api.java.JavaPairRDD;
import org.apache.spark.mllib.evaluation.MulticlassMetrics;
import org.apache.spark.ml.Pipeline;
import org.apache.spark.ml.PipelineModel;
import org.apache.spark.ml.PipelineStage;
import org.apache.spark.ml.tuning.CrossValidator;
import org.apache.spark.ml.tuning.CrossValidatorModel;
import org.apache.spark.ml.tuning.ParamGridBuilder;
import org.apache.spark.ml.param.ParamMap;
import org.apache.spark.ml.evaluation.MulticlassClassificationEvaluator;
import java.util.Arrays;


public class SparkMLlib{
    public static void main(String[] args){
    
        SparkSession spark = SparkSession
            .builder()
            .appName("DataScientest")
            .getOrCreate();

        Dataset<Row> df_raw = spark.read().option("header", "true").csv("penguins_size.csv");

        // MT: il y a besoin de caster les colonnes avant d'aller plus loin

        df_raw = df_raw.select(col("species").cast("string"),
                col("island").cast("string"),
                col("culmen_length_mm").cast("long"),
                col("culmen_depth_mm").cast("long"),
                col("flipper_length_mm").cast("long"),
                col("body_mass_g").cast("long"),
                col("sex").cast("string"));

        String[] str1 = {"culmen_length_mm"};
        String[] str2 = {"culmen_depth_mm"};
        String[] str3 = {"flipper_length_mm"};
        String[] str4 = {"body_mass_g"};
        df_raw = df_raw.na().fill(43.922, str1).na().fill(17.151, str2).na().fill(200.915, str3).na().fill(4201.754, str4);

//        df_raw.groupBy("sex").count().show();

        Map< String, String> sex_replace = new HashMap<>();
        sex_replace.put("NA", "MALE");
        sex_replace.put(".", "MALE");

        df_raw = df_raw.na().replace("sex", sex_replace);
//        df_raw.describe().show();
//        df_raw.show();

        StringIndexer indexer = new StringIndexer()
            .setInputCols(new String[] {"species", "island", "sex"})
            .setOutputCols(new String[] {"speciesIndex", "islandIndex", "sexIndex"});
        Dataset<Row> indexed = indexer.fit(df_raw).transform(df_raw);
        indexed.show();
        indexed.describe().show();

        VectorAssembler assembler = new VectorAssembler()
            .setInputCols(new String[] {"culmen_length_mm", "culmen_depth_mm","flipper_length_mm", "body_mass_g"})
            .setOutputCol("features");
        Dataset<Row> assembled = assembler.transform(indexed);
        assembled.select("features").show();

        StandardScaler scaler = new StandardScaler()
            .setInputCol("features")
            .setOutputCol("scaledFeatures")
            .setWithStd(true)
            .setWithMean(false);
        StandardScalerModel scalerModel = scaler.fit(assembled);
        Dataset<Row> scaled = scalerModel.transform(assembled);
        scaled.show();
        scaled.describe().show();

        VectorAssembler assembler_fin = new VectorAssembler()
            .setInputCols(new String[] {"scaledFeatures", "islandIndex", "sexIndex"})
            .setOutputCol("big_features");
        Dataset<Row> data = assembler_fin.transform(scaled).select("speciesIndex", "big_features");
        data = data.withColumnRenamed("speciesIndex", "label");
        data = data.withColumnRenamed("big_features", "features");
        data.show();

        LogisticRegression lr = new LogisticRegression();
        LogisticRegressionModel lrModel = lr.fit(data);

        JavaRDD<Row> data_rdd = data.toJavaRDD();
        JavaPairRDD< Object, Object> predictionAndLabels = data_rdd.mapToPair(p ->
            new Tuple2<>(lrModel.predict(p.getAs(1)), p.getAs(0)));
        MulticlassMetrics metrics = new MulticlassMetrics(predictionAndLabels.rdd());
        System.out.format("Weighted precision = %f\n", metrics.weightedPrecision());

        /* =================================== */
        /* CETTE FOIS NOUS REFAISONS MAIS AVEC */ 
        /* UNE IMPLEMENTATION D'UNE PIPELINE   */
        /* =================================== */

        StringIndexer indexer2 = new StringIndexer()
            .setInputCols(new String[] {"species", "island", "sex"})
            .setOutputCols(new String[] {"label", "islandIndex", "sexIndex"});
        Dataset<Row> indexed2 = indexer2.fit(df_raw).transform(df_raw);
        VectorAssembler assembler2 = new VectorAssembler()
            .setInputCols(new String[] {"islandIndex", "culmen_length_mm", "culmen_depth_mm", "flipper_length_mm", "body_mass_g", "sexIndex"})
            .setOutputCol("features_pre");
        Dataset<Row> data2 = assembler2.transform(indexed2).select("label", "features_pre");
        System.out.println("data2:");
        data2.show();
        
        StandardScaler scaler2 = new StandardScaler()
            .setInputCol("features_pre")
            .setOutputCol("features")
            .setWithStd(true)
            .setWithMean(false);
        LogisticRegression lr2 = new LogisticRegression();

        Pipeline pipeline = new Pipeline().setStages(new PipelineStage[] {scaler2, lr2});

        Dataset<Row>[] data_split = data2.randomSplit(new double[] {0.8, 0.2}, 12345);
        Dataset<Row> train = data_split[0];
        Dataset<Row> test = data_split[1];
        System.out.println("test:");
        test.show();

        PipelineModel model = pipeline.fit(train);
        Dataset<Row> predictions = model.transform(test);
        System.out.println("predictions:");
        predictions.show();

        JavaRDD<Row> predictions_rdd = predictions.toJavaRDD();
        JavaPairRDD< Object, Object> predictionAndLabels2 = predictions_rdd.mapToPair(p ->
            new Tuple2<>(p.getAs(5), p.getAs(0)));
        MulticlassMetrics metrics2 = new MulticlassMetrics(predictionAndLabels2.rdd());
        System.out.format("Weighted precision = %f\n", metrics2.weightedPrecision());

        /* ================== */
        /* VALIDATION CROISEE */ 
        /* ================== */

        ParamMap[] paramGrid = new ParamGridBuilder()
            .addGrid(lr.regParam(), new double[] {1, 0.1, 0.01})
            .build();
        
        CrossValidator cv = new CrossValidator()
            .setEstimator(pipeline)
            .setEvaluator(new MulticlassClassificationEvaluator())
            .setEstimatorParamMaps(paramGrid)
            .setNumFolds(4);  

        CrossValidatorModel cvModel = cv.fit(train);

        Dataset<Row> predictions2 = cvModel.transform(test);
        System.out.println("predictions2:");
        predictions2.show();

        JavaRDD<Row> predictions_rdd2 = predictions2.select("prediction", "label").toJavaRDD();
        JavaPairRDD< Object, Object> predictionAndLabels3 = predictions_rdd2.mapToPair(p -> new Tuple2<>(p.getAs(0), p.getAs(1)));
        MulticlassMetrics metrics3 = new MulticlassMetrics(predictionAndLabels3.rdd());
        System.out.format("Weighted precision = %f\n", metrics3.weightedPrecision());

        System.out.println(Arrays.toString(cvModel.avgMetrics()));
                
    }
}