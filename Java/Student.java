public class Student{
    public static int nbStudent;
    private int id;
    private String mail;
    private boolean isBootcamp;

    public Student(String mail, boolean isBootcamp){
        this.id = nbStudent;
        this.mail = mail;
        this.isBootcamp = isBootcamp;
        nbStudent++;
    }

    public Student(){
        this(null,false);
    }

    public int getId(){
        return this.id;
    }

    public String getMail(){
        return this.mail;
    }

    public boolean isBootcamp(){
        return this.isBootcamp;
    }

    public String toString(){
        String res = "The id of the Student is " + this.id + "\n";
        res += "The mail of the Student is " + this.mail + "\n";
        if(this.isBootcamp)
            res += "The Student is in a Bootcamp";
        else
            res += "The Student is not in a Bootcamp";
        return res;
    }
}