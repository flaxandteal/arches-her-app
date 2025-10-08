import ko from 'knockout';
import TabbedReportViewModel from 'viewmodels/tabbed-report';



export default ko.components.register('tabbed-report', {
        viewModel: TabbedReportViewModel,
        template: { require: 'text!report-templates/tabbed' }
    });