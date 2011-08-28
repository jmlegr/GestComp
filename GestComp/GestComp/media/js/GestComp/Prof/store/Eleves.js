Ext.define('GestComp.Prof.store.Eleves',{
	extend:'Ext.data.Store',
	autoLoad: true,
	requires:['GestComp.Prof.model.Eleve'],
	model:'GestComp.Prof.model.Eleve',
	sorters:[{property:'classe',direction:'DESC'},{property:'nom',direction:'ASC'},'prenom'],
	groupField:'classe',
	listeners:{		
		//'load':function(){GestComp.Message.fireEvent('message',this,'Liste élèves','chargée')}
		}
	
});