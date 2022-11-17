import java.util.ArrayList;

public class Array{

    public static ArrayList<Integer> InsertionSort(ArrayList<Integer> in_Tab){
        
        ArrayList<Integer> inter_Tab = (ArrayList<Integer>)in_Tab.clone();

        for(int i = 1; i < in_Tab.size(); i++){
            Integer buff_x = inter_Tab.get(i);
            Integer j = i;

            while(j>0 && inter_Tab.get(j-1) > buff_x){
                inter_Tab.set(j, inter_Tab.get(j-1));
                j--;
            }

            inter_Tab.set(j, buff_x);
        }

        return inter_Tab;
    }

    public static void main(String[] args){

        String[] arr  = {"premier", "second", "tiers", "quart", "quint"};

        ArrayList<Integer> listInteger = new ArrayList<Integer>();

        ArrayList<String> listString = new ArrayList<String>();

        ArrayList<Student> cohort = new ArrayList<Student>();
        
        for(int i = 0 ; i<arr.length ; i++){
            listInteger.add(i);
            listString.add(arr[i]);
            cohort.add(new Student());
        }

        for(int a : listInteger){
            System.out.println(a);
        }
        
        for(String word : listString){
            System.out.println(word);
        }
        
        for(Student a : cohort){
            System.out.println(a);
        }

        Integer[] table = {1,5,3,7,8,2,0,11,6,4};
        ArrayList<Integer> Table = new ArrayList<Integer>();
        
        for(int i = 0; i <table.length;i++){
            Table.add(table[i]);
        }

        ArrayList<Integer> Table_sorted = InsertionSort(Table);

        for (int a: Table_sorted){
            System.out.println(a);
        }

        System.out.println(Table_sorted);
    }
}