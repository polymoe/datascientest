/* LES IMPORTS */
import org.apache.spark.api.java.JavaRDD;
import org.apache.spark.api.java.JavaSparkContext;
import org.apache.spark.SparkConf;

import java.util.Arrays;
import org.apache.spark.api.java.JavaPairRDD;
import scala.Tuple2;

import org.apache.spark.sql.SparkSession;
import org.apache.spark.SparkContext;
import org.apache.spark.sql.RowFactory;
import org.apache.spark.sql.types.DataTypes;
import org.apache.spark.sql.types.StructField;
import org.apache.spark.sql.types.StructType;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.Dataset;
import static org.apache.spark.sql.functions.col;
import static org.apache.spark.sql.functions.avg;

import org.apache.spark.ml.feature.StringIndexer;
import org.apache.spark.ml.feature.StandardScaler;
import org.apache.spark.ml.feature.StandardScalerModel;
import org.apache.spark.ml.feature.VectorAssembler;
import scala.Tuple2;
import org.apache.spark.ml.regression.LinearRegression;
import org.apache.spark.ml.regression.LinearRegressionModel;
import org.apache.spark.ml.Pipeline;
import org.apache.spark.ml.PipelineModel;
import org.apache.spark.ml.PipelineStage;
import org.apache.spark.ml.evaluation.RegressionEvaluator;
import org.apache.spark.ml.tuning.CrossValidator;
import org.apache.spark.ml.tuning.CrossValidatorModel;
import org.apache.spark.ml.tuning.ParamGridBuilder;
import org.apache.spark.ml.param.ParamMap;
import java.util.Arrays;
import org.apache.spark.mllib.evaluation.MulticlassMetrics;

/* LA CLASSE */
public class eval{
    public static void main(String[] args){

        /* =============== */
        /* PREMIERE PARTIE */
        /* =============== */

        SparkConf conf = new SparkConf().setAppName("eval").setMaster("local");
        JavaSparkContext sc = new JavaSparkContext(conf);
        JavaRDD<String> rawRDD = sc.textFile("housing.data");
        
        Long rawRDD_size = rawRDD.count();
        System.out.println("- Il y a " + rawRDD_size + " lignes dans le RDD.");

        JavaRDD< String[]> RDD = rawRDD.map(line -> line.substring(1).split("\\s+"));
        //RDD.take(10).forEach(line -> System.out.println(Arrays.toString(line)));

        /* comptez le nombre de villes près du fleuve et celles n'étant pas près du fleuve */
        long riverTowns =  RDD.filter(line -> line[3].equals("1")).count();
        System.out.println("- Il y a " + riverTowns + " villes près du fleuve, et " +  (RDD.count()-riverTowns) + " villes qui ne le sont pas.");

        /* comptez par nombre d'occurrences le nombre moyen de pièces par logement */
        JavaPairRDD< Float, Integer> rmRDD = RDD.mapToPair(line -> new Tuple2(Float.parseFloat(line[5]), 1));
        JavaPairRDD< Integer, Float> sumRmRDD = rmRDD.mapToPair(x -> x.swap()).reduceByKey((a, b) -> a + b);
        sumRmRDD.foreach(data -> {System.out.println("- Le nombre moyen de pièces par logement est : "+ data._2()/rawRDD_size);});

        /* affichez les différentes modalités de la variable RAD */
        JavaPairRDD< String, Integer> pairs = RDD.mapToPair(line -> new Tuple2(line[8], 1));
        JavaPairRDD< String, Integer> counts = pairs.reduceByKey((a, b) -> a+b);
        System.out.println("- les différentes modalités de la variable RAD, par nombre décroissant d'occurrences :");
        counts.mapToPair(x -> x.swap()).sortByKey(false).mapToPair(x -> x.swap()).take(15).forEach(line -> System.out.println(line));

        /* =============== */
        /* DEUXIEME PARTIE */
        /* =============== */

        /* création de la Session et récupération du contexte */
        SparkSession spark = SparkSession
            .builder()
            .appName("eval")
            .getOrCreate();

        SparkContext sc_raw  = spark.sparkContext();
        sc = JavaSparkContext.fromSparkContext(sc_raw);

        /* Transformation du RDD en JavaRDD<Row> */
        JavaRDD<Row> RDD_Row = RDD.map(line -> RowFactory.create(line));

        /* établissement du schema */
        StructType schema = DataTypes.createStructType(new StructField[] {
            DataTypes.createStructField("CRIM", DataTypes.StringType, true),
            DataTypes.createStructField("ZN", DataTypes.StringType, true),
            DataTypes.createStructField("INDUS", DataTypes.StringType, true),
            DataTypes.createStructField("CHAS", DataTypes.StringType, true),
            DataTypes.createStructField("NOX", DataTypes.StringType, true),
            DataTypes.createStructField("RM", DataTypes.StringType, true),
            DataTypes.createStructField("AGE", DataTypes.StringType, true),
            DataTypes.createStructField("DIS", DataTypes.StringType, true),
            DataTypes.createStructField("RAD", DataTypes.StringType, true),
            DataTypes.createStructField("TAX", DataTypes.StringType, true),
            DataTypes.createStructField("PTRATIO", DataTypes.StringType, true),
            DataTypes.createStructField("B 1000(Bk - 063)^2", DataTypes.StringType, true),
            DataTypes.createStructField("LSTAT", DataTypes.StringType, true),
            DataTypes.createStructField("MEDV", DataTypes.StringType, true)
        });

        /* création du dataframe à partir du RDD et du schema */
        Dataset<Row> df = spark.createDataFrame(RDD_Row, schema);
        System.out.println("\n- affichage du dataframe :");
        df.show();        

        /* conversion des colonnes au format double */
        df = df.select(col("CRIM").cast("double"),
            col("ZN").cast("double"),
            col("INDUS").cast("double"),
            col("CHAS").cast("double"),
            col("NOX").cast("double"),
            col("RM").cast("double"),
            col("AGE").cast("double"),
            col("DIS").cast("double"),
            col("RAD").cast("double"),
            col("TAX").cast("double"),
            col("PTRATIO").cast("double"),
            col("B 1000(Bk - 063)^2").cast("double"),
            col("LSTAT").cast("double"),
            col("MEDV").cast("double"));

        /* Trois statistiques et fonctions associées */
        System.out.println("\n- Statistique 1-1 : concentration moyenne en oxyde nitrique pour les communes éloignées de la rivière");
        df.filter(col("CHAS").equalTo(0)).select(avg("NOX")).show();

        System.out.println("\n- Statistique 1-2 : concentration moyenne en oxyde nitrique pour les communes au bord de la rivière");
        df.filter(col("CHAS").equalTo(1)).select(avg("NOX")).show();

        System.out.println("\n- Statistique 2 : Décompte des index d'accessibilité aux autoroutes pour les communes à habitations anciennes (>= 50% construires avant 1940)");
        df.filter(col("AGE").geq(50)).groupBy("RAD").count().show();

        System.out.println("\n- Statistique 3-1 : Proportion moyenne de population pauvre dans les communes à habitations anciennes (>= 50% construires avant 1940)");
        df.filter(col("AGE").geq(50)).select(avg("LSTAT")).show();

        System.out.println("\n- Statistique 3-2 : Proportion moyenne de population pauvre dans les communes à habitations récentes (< 50% construires avant 1940)");
        df.filter(col("AGE").lt(50)).select(avg("LSTAT")).show();

        /* Autres statistiques numériques */
        System.out.println("\n- affichage de statistiques numériques :");
        df.describe().show();

        /* ================ */
        /* MACHINE LEARNING */
        /* ================ */

        System.out.println("\n/* ================ */");
        System.out.println("/* MACHINE LEARNING */");
        System.out.println("/* ================ */\n");

        /* Indexation des variables catégorielles */
        StringIndexer indexer = new StringIndexer()
            .setInputCols(new String[] {"CHAS", "RAD"})
            .setOutputCols(new String[] {"CHASIndex", "RADIndex"});

        Dataset<Row> indexed = indexer.fit(df).transform(df);

        /* Assemblage des features */
        VectorAssembler assembler = new VectorAssembler()
            .setInputCols(new String[] {"CRIM", "ZN", "INDUS", "CHASIndex", "NOX", "RM", "AGE", "DIS", "RADIndex", "TAX", "PTRATIO", "B 1000(Bk - 063)^2", "LSTAT"})
            .setOutputCol("features_pre");
        
        Dataset<Row> data = assembler.transform(indexed).select("MEDV", "features_pre");
        data = data.withColumnRenamed("MEDV","label");
        System.out.println("data:");
        data.show();

        /* Préparation de la pipline contenant une standardisation et un modèle de regression linéaire */
        StandardScaler scaler = new StandardScaler()
            .setInputCol("features_pre")
            .setOutputCol("features")
            .setWithStd(true)
            .setWithMean(false);
        
        LinearRegression lr = new LinearRegression();
        Pipeline pipeline = new Pipeline().setStages(new PipelineStage[] {scaler, lr});

        /* séparation en jeux d'entrainement et de test (80/20) */
        Dataset<Row>[] data_split = data.randomSplit(new double[] {0.8, 0.2}, 12345);
        Dataset<Row> train = data_split[0];
        Dataset<Row> test = data_split[1];
        System.out.println("test:");
        test.show();

        /* préparation de la validation croisée */
        ParamMap[] paramGrid = new ParamGridBuilder()
            .addGrid(lr.regParam(), new double[] {1, 0.1, 0.01})
            .addGrid(lr.fitIntercept())
            .addGrid(lr.maxIter(), new int[] {1,10,100})
            .addGrid(lr.elasticNetParam(), new double[] {0, 0.5, 0.8, 1})
            .build();
        
        CrossValidator cv = new CrossValidator()
            .setEstimator(pipeline)
            .setEvaluator(new RegressionEvaluator())
            .setEstimatorParamMaps(paramGrid)
            .setNumFolds(4); 
        
        /* Entrainement de la pipeline */
        CrossValidatorModel cvModel = cv.fit(train);
        
        /* prédictions sur le jeu de test */        
        Dataset<Row> predictions = cvModel.transform(test);
        System.out.println("predictions:");
        predictions.show();

        /* calcul de la précision du modèle */
        JavaRDD<Row> predictions_rdd = predictions.select("prediction", "label").toJavaRDD();
        JavaPairRDD< Object, Object> predictionAndLabels = predictions_rdd.mapToPair(p -> new Tuple2<>(p.getAs(0), p.getAs(1)));
        MulticlassMetrics metrics = new MulticlassMetrics(predictionAndLabels.rdd());
        System.out.format("Weighted precision = %f\n", metrics.weightedPrecision());

        /* affichage des différentes précisions des modèles */
        System.out.println(Arrays.toString(cvModel.avgMetrics()));
        
        Pipeline bestPipeline = (Pipeline) cvModel.bestModel().parent();
        LinearRegression bestlr = (LinearRegression) bestPipeline.getStages()[1];
        System.out.println("\nles meilleurs hyperparamètres sont les suivants :");
        System.out.println("- regParam :" + bestlr.getRegParam());
        System.out.println("- fitIntercept :" + bestlr.getFitIntercept());
        System.out.println("- maxIter :" + bestlr.getMaxIter());
        System.out.println("- elasticNetParam :" + bestlr.getElasticNetParam());

    }
}