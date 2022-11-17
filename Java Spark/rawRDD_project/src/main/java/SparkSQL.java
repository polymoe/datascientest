import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import static org.apache.spark.sql.functions.col;
import org.apache.spark.sql.DataFrameNaFunctions;
import java.util.HashMap;
import java.util.Map;

public class SparkSQL{
    public static void main(String[] args){
    
        SparkSession spark = SparkSession
            .builder()
            .appName("DataScientest")
            .getOrCreate();

        java.util.Map< String, String> optionsMap = new java.util.HashMap< String, String>();
        optionsMap.put("delimiter",",");
        optionsMap.put("header","true");
        Dataset<Row> df = spark.read().options(optionsMap).csv("titanic.csv");

        df.show();
        df.printSchema();
        df.select("Age", "Sex").show();

        Dataset<Row> mini_df = df.select(col("Age").cast("int"),
                                 col("Sex").cast("string"));
        mini_df.printSchema();

        Dataset<Row> df2 = df.select(col("Survived").cast("boolean"),
                             col("Pclass").cast("int"),
                             col("Name").cast("string"),
                             col("Sex").cast("string"),
                             col("Age").cast("int"),
                             col("Siblings/Spouses Aboard").cast("int"),
                             col("Parents/Children Aboard").cast("int"),
                             col("Fare").cast("double"));
        df2.printSchema();

        df2.select("Pclass").distinct().show();

        System.out.println(df2.select("Parents/Children Aboard").distinct().count());

        df2.describe().show();

        df2.groupBy("Survived").count().show();

        df2.groupBy("Survived", "Parents/Children Aboard").count().sort("Parents/Children Aboard", "Survived").show();

        df2.filter(col("Age").leq(20)).groupBy("Survived").count().show();

        df2.withColumn("Young",col("Age").leq(20)).show(10);

        /*================================================================== */
        /* suite du cours, avec nouvelles données contenant des NA à traiter */
        /*================================================================== */

        Dataset<Row> df3 = spark.read().option("header", "true").csv("penguins_size.csv");
        df3.printSchema();

        // MT: il y a besoin de caster les colonnes avant d'aller plus loin

        df3 = df3.select(col("species").cast("string"),
                col("island").cast("string"),
                col("culmen_length_mm").cast("long"),
                col("culmen_depth_mm").cast("long"),
                col("flipper_length_mm").cast("long"),
                col("body_mass_g").cast("long"),
                col("sex").cast("string"));

        String[] col_names = df3.columns();
        int num_cols = col_names.length;
        Row RR = df3.describe().drop("summary").head();
        for (int i = 0; i < num_cols; i++) {
            System.out.println(col_names[i] + ": " + (df3.count()-Integer.parseInt(RR.getString(i))));
        }
        
        df3.select("species").distinct().show();
        df3.select("island").distinct().show();
        df3.select("sex").distinct().show();

        String[] str1 = {"culmen_length_mm"};
        String[] str2 = {"culmen_depth_mm"};
        String[] str3 = {"flipper_length_mm"};
        String[] str4 = {"body_mass_g"};
        Dataset<Row> df4 = df3.na().fill(43.922, str1).na().fill(17.151, str2).na().fill(200.915, str3).na().fill(4201.754, str4);
        df4.describe().show();
        df4.show();

        df4.groupBy("sex").count().show();

        Map< String, String> sex_replace = new HashMap<>();
        sex_replace.put("NA", "MALE");
        sex_replace.put(".", "MALE");

        df4 = df4.na().replace("sex", sex_replace);
        df4.select("sex").distinct().show();

        df4.createOrReplaceTempView("df4View");
        Dataset<Row> sqldf4 = spark.sql("SELECT body_mass_g FROM df4View");
        sqldf4.show();

        Dataset<Row> df5 = df4.sample(false, 0.1, 12345);
        df5.show();
    }
}