public class DataEngineer extends Student{
    private String ipVm;

    public DataEngineer(String mail, String ipVm, boolean isBootcamp){
        super(mail, isBootcamp);
        this.ipVm = ipVm;
    }

    public String getIp(){
        return this.ipVm;
    }

    public String toString(){
        String res = super.toString();
        res += "\n" + "The Student is a Data Engineer";
        return res;
    }
}