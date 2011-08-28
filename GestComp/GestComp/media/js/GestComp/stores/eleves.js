
Ext.define('GestComp.stores.eleves.EleveModel',{
	extend:'Ext.data.Model',
	fields:['id','nom','prenom','classe','groupes','groupesliste'],
	proxy:{
		type:'ajax',
		url:'/utilisateurs/liste_eleves',
		reader: {
            type: 'json',
            root: 'data'
        }
	}
});
GestComp.Eleves = Ext.create('Ext.data.Store',{
	//autoLoad: true,
	model:'GestComp.stores.eleves.EleveModel',
	sorters:[{property:'classe',direction:'DESC'},{property:'nom',direction:'ASC'},'prenom'],
	groupField:'classe',
	listeners:{		
		'load':function(){GestComp.Message.fireEvent('message',this,'Liste élèves','chargée')}
		}
	
});
