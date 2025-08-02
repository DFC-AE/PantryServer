import java.util.Scanner;

public class input {
	public static void main(String[] args){

		Scanner s = new Scanner(System.in);

		while (s.hasNextLine()){
			String line = s.nextLine();	
			System.out.println(line);
		}
	}
}
