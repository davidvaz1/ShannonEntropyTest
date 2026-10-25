import java.util.Scanner;

public class EntropyTest {
    public static void main(String args[]) {
        Scanner sc = new Scanner(System.in);

        String pwd = sc.nextLine();
        if (pwd.equals("EXIT")) 
            System.exit(0);

        int length = pwd.length();
        boolean hasLower = false;
        boolean hasUpper = false;
        boolean hasDigit = false;
        boolean hasSymbol = false;

        int ps = 0;
        for (int i = 0; i < length; i++) {
            char c = pwd.charAt(i);
            if (c >= 'a' && c <= 'z') 
                hasLower = true;
            else if (c >= 'A' && c <= 'Z') 
                hasUpper = true;
            else if (c >= '0' && c <= '9') 
                hasDigit = true;
            else 
                hasSymbol = true;
        }

        if (hasLower) 
            ps += 26;
        if (hasUpper) 
            ps += 26;
        if (hasDigit)
            ps += 10;
        if (hasSymbol) 
            ps += 32;

        double entropy = 0.0;
        if (length > 0 && ps > 0) 
            entropy = length * (Math.log(ps) / Math.log(2));

        int score = 0;
        if (length >= 8) 
            score += 25;
        if (length >= 12) 
            score += 15;
        if (length >= 16)
            score += 10;
        if (hasLower && hasUpper)
            score += 20;
        if (hasDigit) 
            score += 15;
        if (hasSymbol) 
            score += 15;
        if (score > 100)
            score = 100;

        String dataArray[] = {
                String.valueOf(score),
                String.valueOf(Math.round(entropy * 100.0) / 100.0),
                String.valueOf(hasLower),
                String.valueOf(hasUpper),
                String.valueOf(hasDigit),
                String.valueOf(hasSymbol),
                String.valueOf(length)
            };
        int l = dataArray.length;
        for (int i = 0 ; i < l ; i++) {
            System.out.println(dataArray[i]);
        }
    }
}
