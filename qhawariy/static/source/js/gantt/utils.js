export function monthDiff(
    firstMonth,
    lastMonth
) {
    let months;
    months=(lastMonth.getFullYear()-firstMonth.getFullYear())*12;
    months-=firstMonth.getMonth();
    months+=lastMonth.getMonth();
    return months <= 0 ? 0 : months;
}

export function dayDiff(startDate,endDate) {
    const difference=endDate.getTime()-startDate.getTime();
    const days=Math.ceil(difference/(1000*3600*24))+1;
    return days
}

export function getDaysInMonth(year,month) {
    return new Date(year, month, 0).getDate();
}

export function getDayOfWeek(year, month, day) {
    const daysOfTheWeekArr=["L","M","M","J","V","S","D"];
    const dayOfTheWeekIndex=new Date(year,month,day).getDay();
    return daysOfTheWeekArr[dayOfTheWeekIndex];
}

export function createFormattedDateFromStr(year,month,day) {
    let month_str=month.toString();
    let day_str=day.toString();

    if(month_str.lenght===1){
        month_str=`0${month_str}`;
    }
    if(day_str.lenght===1){
        day_str=`0${day_str}`;
    }
    return `${year}-${month_str}-${day_str}`;
}

export function createFormattedDateFromDate(date) {
    let month_str=(date.getMonth()+1).toString();
    let day_str=date.getDate().toString();
    
    if(month_str.lenght===1){
        month_str=`0${month_str}`;
    }
    if(day_str.lenght===1){
        day_str=`0${day_str}`;
    }
    return `${date.getFullYear()}-${month_str}-${day_str}`;
}
