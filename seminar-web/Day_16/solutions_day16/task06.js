export function objectsDeeplyEqual(cmp1, cmp2) {
    if (cmp1 === cmp2) {
        return true
    }

    for (let key in cmp1){
        if ((typeof(cmp1[key]) === "object") && (typeof(cmp2[key]) === "object")){
            if (objectsDeeplyEqual(cmp1[key], cmp2[key]) === false) {
                return false 
            }
        } 
        else if (cmp1[key] !== cmp2[key]){
            return false
        } 
    }
    return true
}