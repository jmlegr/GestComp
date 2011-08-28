
Ext.define('GestComp.affichage.principal.eleve.Infos',{
 	extend:'Ext.Panel',
 	alias:'widget.infoseleve',
    // default options - can be overridden on instantiation
    // Do NOT put arrays or objects here
     border:false
 	//,title:'info eleve'
    // {{{
    // private
    ,initComponent:function() {
        // create config object
        var config = {
        	//title : 'Accès raiipide',
			//layout:'fit',
        	defaults:{autoScroll:true},        	
			detailTpl: new Ext.XTemplate('' +
			'<div >',
			'<table border="0" cellpadding="0" cellspacing="0" width="100%" height="100%">',
				'<tr><td align="center" valign="middle">',
				'<table border="0" cellpadding="2" cellspacing="2" align="center" width="75%" class="cssDetailsTable">',
					'<tr>',
						'<td class="cssDetailsLabel" width="30%">Nom</td>',
						'<td class="cssDetailsData">{[values.nom.toUpperCase()]}</td>',
					'</tr>',
					'<tr>',
						'<td class="cssDetailsLabel" width="30%">Prénom</td>',
						'<td class="cssDetailsData"> {[Ext.String.capitalize(values.prenom)]}</td>',
					'</tr>',
					'<tr>',
						'<td class="cssDetailsLabel" width="30%">Classe</td>',
						'<td class="cssDetailsData">{classe}</td>',
					'</tr>',
					'<tr>',
						'<td class="cssDetailsLabel" width="30%">Groupes</td>',
						'<td class="cssDetailsDataMini">{groupes}</td>',						
					'</tr>',
				'</table>',
				'</td></tr>',
			'</table>',
			'</div>'),
			html:'<div class="cssDefault"><i>Choisissez un élève dans la grille de gauche</i></div>'
			
        }; //eo config
 
 
        // apply config
        Ext.apply(this, Ext.apply(this.initialConfig, config));
 
        // call parent
        GestComp.affichage.principal.eleve.Infos.superclass.initComponent.call(this);
 
    },// eo function initComponent
    updateDetail:function(data) {
    	this.detailTpl.overwrite(this.body,data)
    }
    // }}}
    // {{{
 
 
}); // eo extend