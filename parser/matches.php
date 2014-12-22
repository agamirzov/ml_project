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

    return $teams[trim($str)];
}

function get_digit($str)
{
    return explode(":", $str);
}

function split_date($str)
{
    return explode(".", $str);
}

//$html = file_get_html("http://wildstat.com/p/2301/ch/ENG_1_2009_2010/tbl/1");

$html_strings = array("2007_2008","2008_2009","2009_2010", "2010_2011", "2011_2012", "2012_2013", "2013_2014", "2014_2015");

for($i = 0; $i < count($html_strings); $i++){

    $game_days = 38;

    $html_string = "http://wildstat.com/p/2301/ch/ENG_1_".$html_strings[$i]."/tbl/";
    $file = fopen("../data/matches".$html_strings[$i].".csv","w");

    for($j=1; $j <= $game_days; $j++)
    {
        $index = (string)$j;
        $html = file_get_html($html_string.$index);

        $table = $html->find('table[class=championship]');

        $row_cnt = 0;
        foreach($table[1]->find('tr') as $tr)
        {    
            $row_cnt++;
            if(!(($row_cnt&1) == 0))
            {
                $cell_cnt = 0;

                foreach($tr->find('td') as $td)
                {
                    $cell_cnt++;
                    if($cell_cnt == 2)
                    {
                        $text = $td->find('a');
                        $dates = split_date($text[0]->plaintext);
                        fwrite($file, $dates[0]);
                        fwrite($file, ",");
                        fwrite($file, $dates[1]);
                        fwrite($file, ",");
                        fwrite($file, $dates[2]);
                        fwrite($file, ",");
                    }
                    elseif($cell_cnt == 4 || $cell_cnt == 6)
                    {
                        $text = $td->find('a');
                        $team = get_team_int($text[0]->plaintext);
                        fwrite($file, intval($team));
                        fwrite($file, ",");
                    }
                    elseif($cell_cnt == 8)
                    {
                        $text = $td->find('b');
                        $scores = get_digit($text[0]->plaintext);
                        fwrite($file, intval($scores[0]));
                        fwrite($file, ",");
                        fwrite($file, intval($scores[1]));
                    }
                }
                fwrite($file, "\n");
            }
        }
        fwrite($file, "\n");
    }
    fclose($file);
}

?>