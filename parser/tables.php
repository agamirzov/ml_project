<?php

include('simple_html_dom.php');

function get_team_int($str)
{
    $teams = [
    "Arsenal"              => 1 ,    
    "Aston Villa"          => 2 ,    
    "Birmingham City"      => 3 ,    
    "Blackburn Rovers"     => 4 ,    
    "Blackpool"            => 5 ,    
    "Bolton Wanderers"     => 6 ,    
    "Burnley"              => 7 ,    
    "Cardiff City"         => 8 ,    
    "Chelsea"              => 9 ,    
    "Crystal Palace"       => 10,    
    "Everton"              => 11,    
    "Fulham"               => 12,    
    "Hull City"            => 13,    
    "Leicester City"       => 14,    
    "Liverpool"            => 15,    
    "Manchester City"      => 16,        
    "Manchester United"    => 17,        
    "Newcastle United"     => 18,        
    "Norwich City"         => 19,        
    "Queens Park Rangers"  => 20,
    "Portsmouth"           => 21,    
    "Reading"              => 22,        
    "Southampton"          => 23,        
    "Stoke City"           => 24,        
    "Sunderland"           => 25,          
    "Swansea City"         => 26,          
    "Tottenham Hotspur"    => 27,          
    "West Bromwich Albion" => 28,          
    "West Ham United"      => 29,          
    "Wigan Athletic"       => 30,         
    "Wolverhampton Wanderers"  => 31,      
    "Middlesbrough"        => 32,
    "Derby County"         => 33, 
    ];

    if (strpos($str, 'Liverpool') !== false) {
        return 15;
    }
    return $teams[trim($str)];
}

function get_digit($str)
{
    return explode(" - ", $str);
}

$html_strings = array("2007_2008","2008_2009","2009_2010", "2010_2011", "2011_2012", "2012_2013", "2013_2014", "2014_2015");

for($i = 0; $i < count($html_strings); $i++)
{    
    $game_days = 38;

    $html_string = "http://wildstat.com/p/2301/ch/ENG_1_".$html_strings[$i]."/tbl/";
    $file = fopen("../data/tables".$html_strings[$i].".csv","w");

    fwrite($file, "match_day,standing,team,games,wins,draws,losses,scored,missed,points,home_wins,home_draws,home_losses,home_scored,home_missed,home_points,away_wins,away_draws,away_losses,away_scored,away_missed,away_points\n");
    for($j=1; $j <= $game_days; $j++)
    {
        $index = (string)$j;
        $html = file_get_html($html_string.$index);

        foreach($html->find('table[cellpadding=2]') as $tbl)
        {
            $row_cnt = 0;
            foreach($tbl->find('tr') as $tr)
            {    
                $row_cnt += 1;

                if($row_cnt > 2 && $row_cnt !== 6 && $row_cnt !== 21)
                {
                    fwrite($file, intval($j));
                    fwrite($file, ","); 
                    $cell_cnt = 0;
                    foreach($tr->find('td') as $td)
                	{
                        if($td->plaintext != "")
                        {
                            $cell_cnt++;

                            if($cell_cnt == 2)
                            {      
                                fwrite($file, get_team_int($td->plaintext));
                            }
                            elseif($cell_cnt == 7 || $cell_cnt == 12 || $cell_cnt == 17)
                            {
                                $digit = get_digit($td->plaintext);

                                fwrite($file, floatval($digit[0]));
                                fwrite($file, ",");
                                fwrite($file, floatval($digit[1]));
                            }
                            else
                            {
                                fwrite($file, floatval($td->plaintext));
                            }
                            if($cell_cnt == 18)
                            {
                                fwrite($file, "\n");
                            }
                            else
                            {
                                fwrite($file, ",");
                            }
                        }
                    }
            	}
            }
        }
        fwrite($file, "\n");
    }
    fclose($file);
}

?>