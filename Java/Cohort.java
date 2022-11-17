public class Cohort {
    public String mail;
    public int id;
    public Student[] arr;
    public static int nbCohort = 0;

    // constructeur avec 2 arguments
    public Cohort(String mail, int nbCohort){
        nbCohort++;
        this.mail = mail;
        this.id = nbCohort;
        this.arr = new Student[nbCohort];
    }

    // constructeur sans arguments
    public Cohort(){
        this(null, 0);
    }

    // Pour les getteurs

    public int getId(){
        return this.id;
    }

    public String getMail(){
        return this.mail;
    }

    public Student[] getStudent(){
        return this.arr;
    }

    public static void main(String[] args){
        Cohort DE = new Cohort();
    }
}