const initDeleteMemo = document.getElementById('btn-init-delete-memo')
const memoid = document.getElementById('memoid').value
const deleteMemoBtn = document.getElementById('delete-memo-btn')

console.log(memoid)

initDeleteMemo.addEventListener('click', function(){
    transitionModal('delete-memo-modal')
})


deleteMemoBtn.addEventListener("click", function(){
    fetch(`/memo/delete/${memoid}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getcsrfToken()
        }
    }).then(response => response.json())
    .then(data=>{
        if(data.status===200){
            showToast({
                style: 'success',
                message: 'Memo deleted successfully',
                duration: 2000,
                onfinshed: ()=>{
                    window.location.href= '/memo/list/'
                }
            })
        }
        else{
            showToast({
                style: 'error',
                message: `An error occured: ${data.message}`,
                duration: 4000
            })
        }
    })
    console.log(getcsrfToken())
})

