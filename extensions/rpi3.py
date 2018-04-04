"""OSF directives related to the RPi3."""

from docutils import nodes

from core import OsfDirective
from core import linux_artifact


class OsfRPi3LinksDirective(OsfDirective):
    '''Directive class for generating links to versioned artifacts.
    '''

    def run(self):
        config = self.get_config()
        version = config.osf_subscriber_version
        if version.startswith('git-'):
            version = 'latest'

        def art_ref(tag, artifact):
            path = 'supported-raspberrypi3-64/{}'.format(artifact)
            return self.build_link('{} ({})'.format(artifact, tag),
                                   linux_artifact(version, path))

        # Paragraph linking to the release.
        links_para = nodes.paragraph()

        # Link to file to get for the release.
        link = art_ref('GZipped WIC format',
                       'lmp-gateway-image-raspberrypi3-64.img.gz')
        links_para += link

        return [links_para]