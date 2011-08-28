Ext.define('GestComp.Prof.model.Eleve',{
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