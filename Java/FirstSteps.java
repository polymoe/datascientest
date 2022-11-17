public class FirstSteps{

    public static int plus(int a, int b){
        return a + b;
    }
    
    public static int plusOne(int a){
        return plus(a, 1);
    }

    public static void main(String[] args){

        // Définition de la variable "a" de type "int"
        int a = 1;
        System.out.println(a);

        // Assignation d'une nouvelle valeur
        a = 2;
        System.out.println(a);

        int b = 2;
        int c = 8;

        int d = plus(b, 1);

        int e = plusOne(c);

        System.out.println(d);
        System.out.println(e);

        String firstname = args[0];
        String lastname = args[1];
        System.out.println("Hello " + firstname + " " + lastname);

    }
}