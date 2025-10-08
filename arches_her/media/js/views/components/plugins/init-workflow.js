import { generateArchesURL } from '@/arches/utils/generate-arches-url.ts';
import ko from 'knockout';
import arches from 'arches';

var InitWorkflow = function(params) {
        this.workflows = params.workflows.map(function(wf){
            wf.url = "/arches-her" + generateArchesURL('arches:plugin')(wf.slug);
            return wf;
        }, this);
    };

export default ko.components.register('init-workflow', {
        viewModel: InitWorkflow,
        template: { require: 'text!templates/views/components/plugins/init-workflow.htm' }
    });