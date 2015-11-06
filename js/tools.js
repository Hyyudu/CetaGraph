function showhide(id, action, itemname)	{
	if (id == 0)	{
		open_selector = '.opener'
		hidden_selector = '.'+itemname
		close_selector = '.closer'
	}
	else	{
		open_selector = "#opener_"+id
		hidden_selector = "#"+itemname+"_"+id
		close_selector = '#closer_'+id

	}
	if (action==1)	{
		$(open_selector).hide();
		$(hidden_selector).removeClass('hidden')
		$(close_selector).show()
		if (id == 0)	{
			$('#show_all_'+itemname).hide()
			$('#hide_all_'+itemname).show()
		}
	}
	else	{
		$(open_selector).show();
		$(hidden_selector).addClass('hidden')
		$(close_selector).hide()
		if (id == 0)	{
			$('#show_all_'+itemname).show()
			$('#hide_all_'+itemname).hide()
		}
	}
	return false;
}

